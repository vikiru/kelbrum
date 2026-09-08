"""Assemble deterministic feature blocks from canonical Polars data."""

from pathlib import Path

import numpy as np
import polars as pl

from anime_catalogue import order_catalogue_frame
from features.blocks import FeatureBlock, FeatureBundle
from features.config import FeatureConfig
from features.encoders import episode_buckets, synopsis_embeddings, year_buckets
from features.synopsis import LatentConfig, TfidfConfig, bm25, lsa, nmf, tfidf
from features.tag_assignment import MANUAL_TAG_ASSIGNMENTS
from features.tags import apply_tag_assignments
from normalization.encoders import bucketize, multi_hot, one_hot
from normalization.policy import apply_missing_policy
from normalization.scalers import transform


def assemble_features(
    frame: pl.DataFrame,
    *,
    config: FeatureConfig,
    embedding_cache: Path | None = None,
    synopsis_embedding_matrix: np.ndarray | None = None,
    source_artifact_sha256: str | None = None,
) -> FeatureBundle:
    """Build aligned categorical, set, text, time, and episode blocks."""
    required = {
        'mal_id',
        'anime_type',
        'source',
        'year',
        'episodes',
        'duration_minutes',
        'rating',
        'genres',
        'themes',
        'demographics',
        'studios',
        'studio_ids',
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f'feature assembly requires columns: {", ".join(missing)}')
    if 'synopsis_features' not in frame.columns:
        raise ValueError('feature assembly requires synopsis_features')
    ordered = order_catalogue_frame(frame)
    anime_ids = ordered['mal_id'].to_numpy().astype(np.int64, copy=False)
    blocks: list[FeatureBlock] = []
    categorical_columns = ('anime_type', 'source', 'rating')
    for column in categorical_columns:
        raw_values = ordered[column].to_list()
        values, names = one_hot(raw_values)
        available = np.asarray(
            [bool(value and value.strip().lower() not in {'unknown', 'n/a', 'not available'}) for value in raw_values],
            dtype=bool,
        )
        blocks.append(FeatureBlock(column, 'one-hot', values, names, (column,), available))
    set_columns = ('genres', 'themes', 'demographics')
    for column in set_columns:
        values, names = multi_hot(ordered[column].to_list())
        blocks.append(FeatureBlock(column, 'multi-hot', values, names, (column,)))
    tag_assignments = apply_tag_assignments(anime_ids, MANUAL_TAG_ASSIGNMENTS)
    tag_values, tag_names = multi_hot([tag_assignments.get(int(anime_id), ()) for anime_id in anime_ids])
    blocks.append(FeatureBlock('tags', 'multi-hot', tag_values, tag_names, ('tags',)))
    if config.include_studios:
        values, names = multi_hot(ordered['studios'].to_list())
        blocks.append(FeatureBlock('studios', 'multi-hot', values, names, ('studios',)))
    episode_values, episode_names = episode_buckets(ordered['episodes'].to_list(), boundaries=config.episode_boundaries)
    blocks.append(
        FeatureBlock(
            'episodes-bucket',
            'one-hot',
            episode_values,
            episode_names,
            ('episodes',),
            np.asarray([value is not None and value >= 1 for value in ordered['episodes'].to_list()], dtype=bool),
        )
    )
    year_values, year_names = year_buckets(ordered['year'].to_list(), boundaries=config.year_boundaries)
    blocks.append(
        FeatureBlock(
            'year-bucket',
            'one-hot',
            year_values,
            year_names,
            ('year',),
            np.asarray(
                [value is not None and value >= config.year_boundaries[0] for value in ordered['year'].to_list()],
                dtype=bool,
            ),
        )
    )
    duration_values, duration_names = bucketize(
        ordered['duration_minutes'].to_list(), boundaries=config.duration_boundaries, missing_below=0
    )
    blocks.append(
        FeatureBlock(
            'duration-bucket',
            'one-hot',
            duration_values,
            duration_names,
            ('duration_minutes',),
            np.asarray(
                [value is not None and value >= 0 for value in ordered['duration_minutes'].to_list()], dtype=bool
            ),
        )
    )
    numeric_columns = ['year', 'episodes', 'duration_minutes']
    if config.include_quality_features:
        score_values, score_names = bucketize(
            ordered['score'].to_list(), boundaries=config.score_boundaries, missing_below=0
        )
        score_names = (*score_names[:-1], '9-10')
        blocks.append(
            FeatureBlock(
                'score-bucket',
                'one-hot',
                score_values,
                score_names,
                ('score',),
                np.asarray([value is not None and value >= 0 for value in ordered['score'].to_list()], dtype=bool),
            )
        )
        numeric_columns.append('score')
    numeric = ordered.select(numeric_columns).to_numpy().astype(np.float64, copy=False)
    numeric_dimension_available = np.isfinite(numeric)
    numeric = apply_missing_policy(numeric, config.numeric_missing_policy)
    numeric = np.column_stack(
        [
            transform(numeric[:, index], config.numeric_transforms.get(column, ()))
            for index, column in enumerate(numeric_columns)
        ]
    )
    blocks.append(
        FeatureBlock(
            'numeric',
            'numeric',
            numeric,
            tuple(numeric_columns),
            tuple(numeric_columns),
            dimension_available=numeric_dimension_available,
        )
    )
    synopsis_texts = ordered['synopsis_features'].to_list()
    synopsis_config = TfidfConfig(
        ngram_range=config.synopsis_ngram_range,
        sublinear_tf=config.synopsis_sublinear_tf,
        stop_words=config.synopsis_stop_words,
        min_df=config.synopsis_min_df,
        max_df=config.synopsis_max_df,
        max_features=config.synopsis_max_features,
    )
    synopsis_features = tfidf(synopsis_texts, synopsis_config)
    blocks.append(
        FeatureBlock(
            'synopsis-tfidf', 'tfidf', synopsis_features.matrix, synopsis_features.vocabulary, ('synopsis_features',)
        )
    )
    latent_config = LatentConfig(dimensions=config.latent_dimensions, max_iter=config.latent_max_iter)
    if config.include_bm25:
        bm25_features = bm25(synopsis_texts)
        blocks.append(
            FeatureBlock(
                'synopsis-bm25', 'bm25', bm25_features.matrix, bm25_features.vocabulary, ('synopsis_features',)
            )
        )
    if config.include_lsa:
        values = lsa(synopsis_features, latent_config)
        blocks.append(
            FeatureBlock(
                'synopsis-lsa',
                'lsa',
                values,
                tuple(f'dimension-{i}' for i in range(values.shape[1])),
                ('synopsis_features',),
            )
        )
    if config.include_nmf:
        values = nmf(synopsis_features, latent_config)
        blocks.append(
            FeatureBlock(
                'synopsis-nmf',
                'nmf',
                values,
                tuple(f'dimension-{i}' for i in range(values.shape[1])),
                ('synopsis_features',),
            )
        )
    if config.embedding_model is not None:
        values = synopsis_embedding_matrix
        if values is None:
            values = synopsis_embeddings(
                synopsis_texts,
                model_name=config.embedding_model_path or config.embedding_model,
                cache_path=embedding_cache,
                ordered_ids=anime_ids,
                source_snapshot_id=config.source_snapshot_id,
                logical_model_name=config.embedding_model,
                source_artifact_sha256=source_artifact_sha256,
                local_only=config.embedding_local_only,
            )
        if values.ndim != 2 or values.shape[0] != anime_ids.size:
            raise ValueError('synopsis embedding matrix must align with the feature rows')
        blocks.append(
            FeatureBlock(
                'synopsis-embedding',
                'embedding',
                values,
                tuple(f'dimension-{i}' for i in range(values.shape[1])),
                ('synopsis_features',),
                np.asarray([bool(text and text.strip()) for text in synopsis_texts], dtype=bool),
            )
        )
    return FeatureBundle(anime_ids, tuple(blocks))
