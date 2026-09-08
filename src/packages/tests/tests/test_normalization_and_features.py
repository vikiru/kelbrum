import numpy as np
import pytest
from scipy.sparse import csr_matrix

from features.blocks import FeatureBlock, FeatureBundle
from features.synopsis import TfidfConfig, clean_synopses, tfidf
from normalization.encoders import bucketize, clean_labels, multi_hot, one_hot
from normalization.scalers import FittedState, MinMaxScaler, transform
from recommender.weighted_v2 import WeightedV2Index, weighted_distance


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

    assert restored == scaler.state
    assert np.allclose(scaler.transform(values).ravel(), [0.0, 0.5, 1.0])
    assert np.allclose(transform(values, ('minmax',)).ravel(), [0.0, 0.5, 1.0])


def test_numeric_transforms_reject_invalid_values() -> None:
    with pytest.raises(ValueError, match='finite'):
        transform(np.asarray([1.0, np.nan]), ('minmax',))
    with pytest.raises(ValueError, match='non-negative'):
        transform(np.asarray([-1.0, 1.0]), ('log1p',))


def test_feature_bundle_requires_unique_aligned_rows_and_reports_availability() -> None:
    values = csr_matrix([[1.0, 0.0], [0.0, 0.0]])
    block = FeatureBlock('genres', 'multi-hot', values, ('Drama', 'Sports'), ('genres',))
    bundle = FeatureBundle(np.asarray([10, 20], dtype=np.int64), (block,))

    assert block.availability().tolist() == [True, False]
    assert bundle.matrix().shape == (2, 2)

    with pytest.raises(ValueError, match='unique'):
        FeatureBundle(np.asarray([10, 10], dtype=np.int64), (block,))


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
                np.asarray([False, True]),
            ),
        ),
    )

    results = WeightedV2Index(
        bundle,
        weights={'genres': 0.5, 'year-bucket': 0.5},
        metrics={'genres': 'jaccard', 'year-bucket': 'dice'},
    ).rank(0, limit=1)

    assert results == ((20, 1.0),)


def test_weighted_distance_omits_numeric_weight_without_shared_dimensions() -> None:
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
                dimension_available=np.asarray([[True, False], [False, True]]),
            ),
        ),
    )

    assert weighted_distance(bundle, 0, 1, weights={'genres': 0.5, 'numeric': 0.5}) == 0.0


def test_weighted_distance_omits_matching_missing_bucket_weight() -> None:
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
                np.asarray([False, False]),
            ),
        ),
    )

    assert weighted_distance(bundle, 0, 1, weights={'genres': 0.5, 'year-bucket': 0.5}) == 0.0


def test_synopsis_features_clean_text_and_preserve_row_alignment() -> None:
    texts = ['  quiet\nforest  ', None, 'space adventure']

    assert clean_synopses(texts) == ['quiet forest', '', 'space adventure']
    features = tfidf(texts, TfidfConfig(min_df=1, max_df=1.0))

    assert features.matrix.shape[0] == len(texts)
    assert features.matrix.shape[1] == len(features.vocabulary)
    assert np.allclose(np.asarray(features.matrix.sum(axis=1)).ravel()[1], 0.0)
