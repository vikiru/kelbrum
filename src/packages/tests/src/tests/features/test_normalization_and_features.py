import numpy as np
import polars as pl
import pytest
from scipy.sparse import csr_matrix

import features.embeddings as embeddings
from features.assemble import FeatureAssemblyRequest, assemble_features
from features.blocks import FeatureBlock, FeatureBundle
from features.cache import (
    configuration_hash,
    decode_metadata,
    encode_metadata,
    new_cache_metadata,
    validate_cache_metadata,
)
from features.categorical_blocks import CategoricalEncoding, CategoricalProperty, build_categorical_blocks
from features.composition import FeatureAssemblyPlan, FeatureStage
from features.config import EmbeddingModel, EmbeddingSource, FeatureConfig
from features.numeric import build_numeric_blocks, normalize_numeric
from features.synopsis import TfidfConfig, bm25, clean_synopses, tfidf
from features.text_blocks import build_text_blocks
from normalization.encoders import bucketize, clean_labels, multi_hot, one_hot
from normalization.policy import MissingPolicy
from normalization.scalers import (
    FittedState,
    MaxAbsScaler,
    MinMaxScaler,
    RobustScaler,
    StandardScaler,
    TransformName,
    restore,
    transform,
)
from recommender.metrics import Similarity, SimilarityOperands, similarity_score, vectorized_similarity
from recommender.paths import SynopsisPathIndex
from recommender.plan import RecommenderPlan
from recommender.properties import SimilarityProperty
from recommender.weighted_v2 import WeightedV2Index, weighted_similarity


def test_categorical_encoders_clean_labels_and_preserve_rows() -> None:
    assert clean_labels([' Drama ', '', None, 'Drama']) == ('Drama',)

    one_hot_values, one_hot_names = one_hot(['TV', None, 'Movie'])
    multi_hot_values, multi_hot_names = multi_hot([['Action', 'Drama'], None, ['Drama']])

    assert one_hot_values.shape == (3, 3)
    assert one_hot_names == ('', 'Movie', 'TV')
    assert multi_hot_values.shape == (3, 2)
    assert multi_hot_names == ('Action', 'Drama')


def test_bucketize_handles_boundaries_and_missing_values() -> None:
    matrix, labels = bucketize([None, 1, 12, 13, 50], boundaries=(1, 12, 50), missing_below=1)

    assert labels == ('missing', '1-11', '12-49', '50+')
    assert matrix.getnnz(axis=1).tolist() == [1, 1, 1, 1, 1]
    assert np.asarray(matrix.argmax(axis=1)).ravel().tolist() == [0, 1, 2, 2, 3]


def test_numeric_transforms_are_deterministic_and_round_trip_fitted_state() -> None:
    values = np.asarray([0.0, 5.0, 10.0])
    scaler = MinMaxScaler(source_name='score').fit(values)
    assert scaler.state is not None
    restored = FittedState.from_json(scaler.state.to_json())
    restored_scaler = restore(restored)

    assert restored == scaler.state
    assert np.allclose(scaler.transform(values).ravel(), [0.0, 0.5, 1.0])
    assert np.allclose(restored_scaler.transform(values).ravel(), [0.0, 0.5, 1.0])
    assert np.allclose(transform(values, ('minmax',)).ravel(), [0.0, 0.5, 1.0])
    assert np.allclose(transform(values, (TransformName.MINMAX,)).ravel(), [0.0, 0.5, 1.0])


def test_numeric_transforms_reject_invalid_values() -> None:
    with pytest.raises(ValueError, match='finite'):
        transform(np.asarray([1.0, np.nan]), ('minmax',))
    with pytest.raises(ValueError, match='non-negative'):
        transform(np.asarray([-1.0, 1.0]), ('log1p',))


def test_numeric_transforms_define_constant_columns_and_input_shape() -> None:
    values = np.asarray([3.0, 3.0, 3.0], dtype=np.float64)

    assert np.allclose(MinMaxScaler().fit_transform(values), 0.0)
    assert np.allclose(RobustScaler().fit_transform(values), 0.0)
    assert np.allclose(StandardScaler().fit_transform(values), 0.0)
    assert np.allclose(MaxAbsScaler().fit_transform(values), 1.0)
    assert MinMaxScaler().fit_transform(values).dtype == np.float64

    with pytest.raises(ValueError, match='must not be empty'):
        transform(np.asarray([], dtype=np.float64), ('minmax',))
    with pytest.raises(ValueError, match='one- or two-dimensional'):
        transform(np.zeros((1, 1, 1)), ('minmax',))


def test_feature_bundle_requires_unique_aligned_rows_and_reports_availability() -> None:
    values = csr_matrix([[1.0, 0.0], [0.0, 0.0]])
    block = FeatureBlock('genres', 'multi-hot', values, ('Drama', 'Sports'), ('genres',))
    bundle = FeatureBundle(np.asarray([10, 20], dtype=np.int64), (block,))

    assert block.availability().tolist() == [True, False]
    assert bundle.matrix().shape == (2, 2)

    with pytest.raises(ValueError, match='unique'):
        FeatureBundle(np.asarray([10, 10], dtype=np.int64), (block,))


def test_feature_block_exposes_dense_rows_for_scalar_calculations() -> None:
    block = FeatureBlock(
        'genres',
        'multi-hot',
        csr_matrix([[1.0, 0.0], [0.0, 1.0]]),
        ('Drama', 'Comedy'),
        ('genres',),
    )

    assert np.array_equal(block.dense_row(1), np.asarray([0.0, 1.0]))


def test_numeric_builder_owns_optional_quality_block() -> None:
    frame = pl.DataFrame(
        {
            'year': [2020, None],
            'episodes': [12, 24],
            'duration_minutes': [24, None],
            'score': [8.5, None],
        }
    )

    blocks = build_numeric_blocks(frame, config=FeatureConfig(include_quality_features=True))

    assert tuple(block.name for block in blocks) == (
        'episodes-bucket',
        'year-bucket',
        'duration-bucket',
        'score-bucket',
        'numeric',
    )
    numeric = blocks[-1]
    assert numeric.column_names == ('year', 'episodes', 'duration_minutes', 'score')
    assert numeric.dimension_available is not None
    assert numeric.dimension_available.tolist() == [[True, True, True, True], [False, True, False, False]]
    assert numeric.row_available is not None
    assert numeric.row_available.tolist() == [True, True]


def test_numeric_normalization_preserves_missing_values_through_transforms() -> None:
    config = FeatureConfig(numeric_missing_policy=MissingPolicy.PRESERVE)

    normalized = normalize_numeric(np.asarray([None, 2020], dtype=np.float64), 'year', config)

    assert np.isnan(normalized[0, 0])
    assert normalized[1, 0] == 0.0


def test_categorical_builder_allows_curated_tags_to_be_replaced_or_disabled() -> None:
    frame = pl.DataFrame(
        {
            'anime_type': ['TV', 'Movie'],
            'source': ['Manga', 'Original'],
            'rating': ['PG-13', 'G'],
            'genres': [['Action'], ['Drama']],
            'themes': [['Mecha'], []],
            'demographics': [[], ['Shounen']],
            'studios': [['A'], ['B']],
        }
    )
    anime_ids = np.asarray([1, 2], dtype=np.int64)

    blocks = build_categorical_blocks(frame, anime_ids, include_studios=False, tag_assignments=())

    assert tuple(block.name for block in blocks) == (
        'anime_type',
        'source',
        'rating',
        'genres',
        'themes',
        'demographics',
        'tags',
    )
    assert blocks[-1].values.shape[0] == anime_ids.size


def test_categorical_builder_composes_only_declared_properties_in_declared_order() -> None:
    frame = pl.DataFrame({'genres': [['Action'], ['Drama']], 'rating': ['G', 'PG']})
    properties = (
        CategoricalProperty('genres', CategoricalEncoding.MULTI_HOT, source_column='genres'),
        CategoricalProperty('rating', CategoricalEncoding.ONE_HOT, source_column='rating'),
    )

    blocks = build_categorical_blocks(
        frame,
        np.asarray([1, 2], dtype=np.int64),
        include_studios=False,
        properties=properties,
    )

    assert tuple(block.name for block in blocks) == ('genres', 'rating')


def test_feature_assembly_accepts_a_custom_stage_with_its_own_column_boundary() -> None:
    frame = pl.DataFrame({'mal_id': [2, 1], 'custom_value': [20.0, 10.0]})
    observed: list[tuple[str, int, int]] = []

    def build_custom_stage(
        ordered_frame: pl.DataFrame, _anime_ids: np.ndarray, _config: FeatureConfig
    ) -> tuple[FeatureBlock, ...]:
        return (
            FeatureBlock(
                'custom',
                'numeric',
                ordered_frame['custom_value'].to_numpy().reshape((-1, 1)),
                ('custom_value',),
                ('custom_value',),
            ),
        )

    bundle = assemble_features(
        frame,
        FeatureAssemblyRequest(
            config=FeatureConfig(),
            plan=FeatureAssemblyPlan((FeatureStage('custom', frozenset({'custom_value'}), build_custom_stage),)),
            stage_observer=lambda name, block_count, row_count: observed.append((name, block_count, row_count)),
        ),
    )

    assert tuple(bundle.anime_ids) == (1, 2)
    assert tuple(block.name for block in bundle.blocks) == ('custom',)
    assert observed == [('custom', 1, 2)]


def test_numeric_stage_accepts_a_replaceable_normalizer() -> None:
    frame = pl.DataFrame(
        {
            'year': [2000, 2001],
            'episodes': [12, 24],
            'duration_minutes': [20, 25],
            'score': [7.0, 8.0],
        }
    )

    def normalize_to_half(values: np.ndarray, _column: str, _config: FeatureConfig) -> np.ndarray:
        return np.full(values.shape, 0.5)

    blocks = build_numeric_blocks(frame, config=FeatureConfig(), normalizer=normalize_to_half)

    assert isinstance(blocks[-1].values, np.ndarray)
    assert np.allclose(blocks[-1].values, 0.5)


def test_text_builder_composes_optional_bm25_without_embedding_work() -> None:
    config = FeatureConfig(
        include_bm25=True,
        synopsis_min_df=1,
        synopsis_max_df=1.0,
    )

    blocks = build_text_blocks(['quiet forest', 'space adventure'], np.asarray([1, 2]), config=config)

    assert tuple(block.name for block in blocks) == ('synopsis-tfidf', 'synopsis-bm25')
    assert all(block.values.shape[0] == 2 for block in blocks)


def test_embedding_model_reference_distinguishes_local_and_remote_sources() -> None:
    local = EmbeddingModel(source=EmbeddingSource.LOCAL, identifier='/models/minilm')
    remote = EmbeddingModel(source=EmbeddingSource.REMOTE, identifier='org/minilm', revision='main')

    assert local.local_only
    assert not remote.local_only


def test_text_builder_requires_pipeline_owned_embeddings() -> None:
    config = FeatureConfig(
        embedding=EmbeddingModel(source=EmbeddingSource.REMOTE, identifier='org/minilm'),
        synopsis_min_df=1,
        synopsis_max_df=1.0,
    )

    with pytest.raises(ValueError, match='synopsis_embedding_matrix'):
        build_text_blocks(['quiet forest'], np.asarray([1]), config=config)


def test_bm25_downweights_terms_that_occur_in_every_document() -> None:
    features = bm25(['common rare', 'common'], k1=1.5, b=0.75)
    common_index = features.vocabulary.index('common')
    rare_index = features.vocabulary.index('rare')

    assert features.matrix.toarray()[0, rare_index] > features.matrix.toarray()[0, common_index]


def test_feature_cache_identity_is_deterministic_and_rejects_schema_changes() -> None:
    configuration = {'include_bm25': True, 'transforms': ('minmax', 'robust')}
    metadata = new_cache_metadata(
        model_name='all-MiniLM-L6-v2',
        ordered_ids=[20, 1],
        source_snapshot_id='snapshot-a',
        configuration=configuration,
    )

    assert configuration_hash(configuration) == configuration_hash(
        {'transforms': ['minmax', 'robust'], 'include_bm25': True}
    )
    assert configuration_hash(configuration, tag_assignment_identity='changed') != configuration_hash(configuration)
    validate_cache_metadata(
        metadata,
        model_name='all-MiniLM-L6-v2',
        ordered_ids=[20, 1],
        source_snapshot_id='snapshot-a',
        configuration=configuration,
    )
    with pytest.raises(ValueError, match='schema'):
        validate_cache_metadata(
            metadata,
            model_name='all-MiniLM-L6-v2',
            ordered_ids=[20, 1],
            source_snapshot_id='snapshot-a',
            configuration=configuration,
            schema_version='feature-cache-v2',
        )

    encoded = encode_metadata(metadata)
    assert encoded == encode_metadata(metadata)
    assert decode_metadata(encoded) == metadata


def test_embedding_cache_miss_reports_optional_model_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def unavailable(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError('model unavailable')

    monkeypatch.setattr(
        embeddings,
        '_embedding_model',
        unavailable,
    )
    monkeypatch.setattr(embeddings, '_embedding_device', lambda: 'cpu')

    with pytest.raises(RuntimeError, match='model unavailable'):
        embeddings.encode_synopsis_embeddings(['text'], model_name='missing-model')


def test_weighted_similarity_omits_missing_bucket_from_available_weight() -> None:
    genre_values = csr_matrix([[1.0], [1.0]])
    year_values = csr_matrix([[1.0, 0.0], [0.0, 1.0]])
    bundle = FeatureBundle(
        np.asarray([10, 20], dtype=np.int64),
        (
            FeatureBlock('genres', 'multi-hot', genre_values, ('Drama',), ('genres',)),
            FeatureBlock(
                'year-bucket',
                'one-hot',
                year_values,
                ('missing', '2000+'),
                ('year',),
                np.asarray([False, True], dtype=bool),
            ),
        ),
    )

    results = WeightedV2Index(
        bundle,
        weights={'genres': 0.5, 'year-bucket': 0.5},
        metrics={'genres': 'jaccard', 'year-bucket': 'dice'},
    ).rank(0, limit=1)

    assert results == ((20, 1.0),)


def test_similarity_score_is_higher_is_better_and_handles_empty_rows() -> None:
    left = np.asarray([1.0, 0.0])
    right = np.asarray([1.0, 1.0])

    assert similarity_score(left, right, Similarity.JACCARD) == 0.5
    assert similarity_score(left, right, Similarity.DICE) == pytest.approx(2 / 3)
    assert similarity_score(np.zeros(2), np.zeros(2), Similarity.COSINE) == 0.0


@pytest.mark.parametrize('metric', [Similarity.JACCARD, Similarity.DICE, Similarity.COSINE])
def test_registered_vectorized_metrics_match_scalar_scores(metric: Similarity) -> None:
    left = np.asarray([1.0, 0.0, 1.0])
    right = np.asarray([1.0, 1.0, 0.0])
    if metric is Similarity.COSINE:
        operands = SimilarityOperands(
            intersections=np.asarray([1.0]),
            left_norms=np.asarray([np.linalg.norm(left)]),
            right_norms=np.asarray([np.linalg.norm(right)]),
        )
    else:
        operands = SimilarityOperands(
            intersections=np.asarray([1.0]),
            left_sizes=np.asarray([2.0]),
            right_sizes=np.asarray([2.0]),
        )

    vectorized = vectorized_similarity(metric, operands)

    assert vectorized[0] == pytest.approx(similarity_score(left, right, metric))


def test_recommender_plan_validates_paths_and_derives_policy_identity() -> None:
    plan = RecommenderPlan(retrieval_paths=('genres', 'themes'))

    assert plan.retrieval_paths == ('genres', 'themes')
    assert plan.has_path('genres')
    assert not plan.has_path('embedding')
    assert plan.identity == RecommenderPlan(retrieval_paths=('genres', 'themes')).identity


@pytest.mark.parametrize('metric', [Similarity.COSINE, Similarity.JACCARD, Similarity.DICE])
def test_weighted_block_scalar_and_vectorized_metrics_match(metric: Similarity) -> None:
    block = FeatureBlock(
        'genres',
        'multi-hot',
        csr_matrix([[1.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 1.0]]),
        ('Drama', 'Comedy', 'Sports'),
        ('genres',),
    )
    index = WeightedV2Index(
        FeatureBundle(np.asarray([10, 20, 30], dtype=np.int64), (block,)),
        weights={'genres': 1.0},
        metrics={'genres': metric},
    )
    prepared = index.blocks['genres']

    assert prepared.similarity(0, 1, metric) == pytest.approx(prepared.similarities(0, metric)[1])
    assert prepared.similarity(0, 1, metric) == pytest.approx(prepared.similarities_many((0,), metric)[0, 1])


def test_weighted_block_masked_numeric_metrics_match_across_execution_modes() -> None:
    block = FeatureBlock(
        'numeric',
        'numeric',
        np.asarray([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]),
        ('year', 'episodes'),
        ('year', 'episodes'),
        dimension_available=np.asarray([[True, False], [True, True], [False, True]], dtype=bool),
    )
    index = WeightedV2Index(
        FeatureBundle(np.asarray([10, 20, 30], dtype=np.int64), (block,)),
        weights={'numeric': 1.0},
        metrics={'numeric': Similarity.MANHATTAN},
    )
    prepared = index.blocks['numeric']

    assert prepared.similarity(0, 1, Similarity.MANHATTAN) == pytest.approx(
        prepared.similarities(0, Similarity.MANHATTAN)[1]
    )
    assert prepared.similarity(0, 1, Similarity.MANHATTAN) == pytest.approx(
        prepared.similarities_many((0,), Similarity.MANHATTAN)[0, 1]
    )


def test_weighted_similarity_rejects_invalid_limits_and_masks() -> None:
    bundle = FeatureBundle(
        np.asarray([10, 20], dtype=np.int64),
        (FeatureBlock('genres', 'multi-hot', csr_matrix([[1.0], [1.0]]), ('Drama',), ('genres',)),),
    )
    index = WeightedV2Index(bundle, weights={'genres': 1.0}, metrics={'genres': 'jaccard'})

    with pytest.raises(ValueError, match='limit must be positive'):
        index.rank(0, limit=0)
    with pytest.raises(ValueError, match='candidate mask'):
        index.rank(0, candidate_mask=np.ones(1, dtype=bool))


def test_weighted_similarity_ties_are_canonical_across_batch_and_streaming_retrieval() -> None:
    bundle = FeatureBundle(
        np.asarray([30, 10, 20], dtype=np.int64),
        (FeatureBlock('genres', 'multi-hot', csr_matrix([[1.0], [1.0], [1.0]]), ('Drama',), ('genres',)),),
    )
    index = WeightedV2Index(bundle, weights={'genres': 1.0}, metrics={'genres': 'jaccard'})

    expected = ((10, 1.0), (20, 1.0))
    assert index.rank(0, limit=2) == expected
    assert index.rank_many_streaming((0,), limit=2, candidate_batch_size=1)[0] == expected
    candidate_mask = np.asarray([False, True, True])
    assert index.rank(0, limit=2, candidate_mask=candidate_mask) == expected
    assert (
        index.rank_many_streaming((0,), limit=2, candidate_batch_size=1, candidate_mask=candidate_mask)[0] == expected
    )


def test_weighted_streaming_ties_use_anime_id_order_for_unsorted_rows() -> None:
    bundle = FeatureBundle(
        np.asarray([20, 30, 10], dtype=np.int64),
        (FeatureBlock('genres', 'multi-hot', csr_matrix([[1.0], [1.0], [1.0]]), ('Drama',), ('genres',)),),
    )
    index = WeightedV2Index(bundle, weights={'genres': 1.0}, metrics={'genres': 'jaccard'})

    expected = index.rank(0, limit=2)

    assert expected == ((10, 1.0), (30, 1.0))
    assert index.rank_many_streaming((0,), limit=2, candidate_batch_size=3)[0] == expected


def test_weighted_similarity_omits_numeric_weight_without_shared_dimensions() -> None:
    bundle = FeatureBundle(
        np.asarray([10, 20], dtype=np.int64),
        (
            FeatureBlock('genres', 'multi-hot', csr_matrix([[1.0], [1.0]]), ('Drama',), ('genres',)),
            FeatureBlock(
                'numeric',
                'numeric',
                np.asarray([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32),
                ('year', 'episodes'),
                ('year', 'episodes'),
                dimension_available=np.asarray([[True, False], [False, True]], dtype=bool),
            ),
        ),
    )

    assert weighted_similarity(bundle, 0, 1, weights={'genres': 0.5, 'numeric': 0.5}) == 1.0


def test_weighted_similarity_omits_matching_missing_bucket_weight() -> None:
    bundle = FeatureBundle(
        np.asarray([10, 20], dtype=np.int64),
        (
            FeatureBlock('genres', 'multi-hot', csr_matrix([[1.0], [1.0]]), ('Drama',), ('genres',)),
            FeatureBlock(
                'year-bucket',
                'one-hot',
                csr_matrix([[1.0, 0.0], [1.0, 0.0]]),
                ('missing', '2000+'),
                ('year',),
                np.asarray([False, False], dtype=bool),
            ),
        ),
    )

    assert weighted_similarity(bundle, 0, 1, weights={'genres': 0.5, 'year-bucket': 0.5}) == 1.0


def test_similarity_properties_can_be_selected_and_reordered_independently() -> None:
    bundle = FeatureBundle(
        np.asarray([10, 20], dtype=np.int64),
        (
            FeatureBlock('genres', 'multi-hot', csr_matrix([[1.0], [1.0]]), ('Drama',), ('genres',)),
            FeatureBlock('year-bucket', 'one-hot', csr_matrix([[1.0, 0.0], [0.0, 1.0]]), ('old', 'new'), ('year',)),
        ),
    )
    properties = (
        SimilarityProperty('year-bucket', 0.5, 'dice'),
        SimilarityProperty('genres', 0.5, 'jaccard', contributes_to_content=True),
    )

    index = WeightedV2Index(bundle, properties=properties)

    assert index.properties == properties
    assert index.rank(0, limit=1) == ((20, 0.5),)
    assert weighted_similarity(bundle, 0, 1, properties=properties) == 0.5


def test_similarity_properties_reject_duplicate_or_non_finite_weights() -> None:
    with pytest.raises(ValueError, match='finite'):
        SimilarityProperty('genres', float('nan'))

    bundle = FeatureBundle(
        np.asarray([10, 20], dtype=np.int64),
        (FeatureBlock('genres', 'multi-hot', csr_matrix([[1.0], [1.0]]), ('Drama',), ('genres',)),),
    )
    duplicate = (SimilarityProperty('genres', 0.5), SimilarityProperty('genres', 0.5))
    with pytest.raises(ValueError, match='unique'):
        WeightedV2Index(bundle, properties=duplicate)


def test_similarity_properties_normalize_metric_names() -> None:
    enum_property = SimilarityProperty('genres', 1.0, Similarity.JACCARD)
    string_property = SimilarityProperty('genres', 1.0, 'jaccard')

    assert enum_property.metric is Similarity.JACCARD
    assert string_property.metric is Similarity.JACCARD

    with pytest.raises(ValueError, match='unsupported similarity metric'):
        SimilarityProperty('genres', 1.0, 'unsupported')


def test_similarity_index_accepts_a_custom_availability_policy() -> None:
    bundle = FeatureBundle(
        np.asarray([10, 20], dtype=np.int64),
        (FeatureBlock('genres', 'multi-hot', csr_matrix((2, 1)), ('Drama',), ('genres',)),),
    )

    def treat_rows_as_available(block: FeatureBlock) -> np.ndarray:
        return np.ones(block.values.shape[0], dtype=bool)

    index = WeightedV2Index(
        bundle,
        properties=(SimilarityProperty('genres', 1.0, 'jaccard', contributes_to_content=True),),
        availability_policy=treat_rows_as_available,
    )

    assert index.rank(0, limit=1) == ()


def test_synopsis_features_clean_text_and_preserve_row_alignment() -> None:
    texts = ['  quiet\nforest  ', None, 'space adventure']

    assert clean_synopses(texts) == ['quiet forest', '', 'space adventure']
    features = tfidf(texts, TfidfConfig(min_df=1, max_df=1.0))

    assert features.matrix.shape[0] == len(texts)
    assert features.matrix.shape[1] == len(features.vocabulary)
    assert np.allclose(np.asarray(features.matrix.sum(axis=1)).ravel()[1], 0.0)


def test_uninformative_synopsis_corpus_returns_aligned_empty_features() -> None:
    texts = ['common text'] * 3

    tfidf_features = tfidf(texts)
    bm25_features = bm25(['the and or'] * 3)

    assert tfidf_features.matrix.shape == (3, 0)
    assert bm25_features.matrix.shape == (3, 0)


@pytest.mark.parametrize('texts', [['single synopsis'], [''], ['the and or']])
def test_tfidf_returns_aligned_empty_features_for_tiny_or_uninformative_corpora(
    texts: list[str],
) -> None:
    features = tfidf(texts)

    assert features.matrix.shape == (len(texts), 0)


def test_synopsis_ties_are_canonical_across_batch_and_streaming_retrieval() -> None:
    index = SynopsisPathIndex([30, 10, 20], ['same text'] * 3)
    index.fit_tfidf(TfidfConfig(min_df=1, max_df=1.0))

    expected = ((10, 1.0), (20, 1.0))
    assert index.rank('tfidf', 0, limit=2) == expected
    assert index.rank_many_streaming('tfidf', (0,), limit=2, candidate_batch_size=1)[0] == expected


def test_synopsis_streaming_ties_use_anime_id_order_for_unsorted_rows() -> None:
    index = SynopsisPathIndex([20, 30, 10], ['same words', 'same words', 'same words'])
    index.fit_embedding_matrix(np.ones((3, 2), dtype=np.float32))

    expected = index.rank('embedding', 0, limit=2)

    assert expected == ((10, pytest.approx(1.0)), (30, pytest.approx(1.0)))
    assert index.rank_many_streaming('embedding', (0,), limit=2, candidate_batch_size=3)[0] == expected
