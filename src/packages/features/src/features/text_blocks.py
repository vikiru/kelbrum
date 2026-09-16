"""Build optional text-derived feature blocks."""

from collections.abc import Sequence

import numpy as np

from features.blocks import FeatureBlock
from features.config import FeatureConfig
from features.synopsis import LatentConfig, TfidfConfig, bm25, lsa, nmf, tfidf

_MATRIX_DIMENSIONS = 2


def build_text_blocks(
    texts: Sequence[str | None],
    anime_ids: np.ndarray,
    *,
    config: FeatureConfig,
    synopsis_embedding_matrix: np.ndarray | None = None,
) -> tuple[FeatureBlock, ...]:
    """Build configured text blocks without filesystem or catalogue access."""
    synopsis_config = TfidfConfig(
        ngram_range=config.synopsis_ngram_range,
        sublinear_tf=config.synopsis_sublinear_tf,
        stop_words=config.synopsis_stop_words,
        min_df=config.synopsis_min_df,
        max_df=config.synopsis_max_df,
        max_features=config.synopsis_max_features,
    )
    synopsis_features = tfidf(texts, synopsis_config)
    blocks = [
        FeatureBlock(
            'synopsis-tfidf',
            'tfidf',
            synopsis_features.matrix,
            synopsis_features.vocabulary,
            ('synopsis_features',),
        )
    ]
    latent_config = LatentConfig(dimensions=config.latent_dimensions, max_iter=config.latent_max_iter)
    if config.include_bm25:
        bm25_features = bm25(texts)
        blocks.append(
            FeatureBlock(
                'synopsis-bm25', 'bm25', bm25_features.matrix, bm25_features.vocabulary, ('synopsis_features',)
            )
        )
    if config.include_lsa:
        values = lsa(synopsis_features, latent_config)
        blocks.append(_latent_block('synopsis-lsa', values))
    if config.include_nmf:
        values = nmf(synopsis_features, latent_config)
        blocks.append(_latent_block('synopsis-nmf', values))
    if config.embedding is not None:
        values = synopsis_embedding_matrix
        if values is None:
            raise ValueError('synopsis_embedding_matrix is required when embeddings are enabled')
        if values.ndim != _MATRIX_DIMENSIONS or values.shape[0] != anime_ids.size:
            raise ValueError('synopsis embedding matrix must align with the feature rows')
        blocks.append(
            FeatureBlock(
                'synopsis-embedding',
                'embedding',
                values,
                tuple(f'dimension-{index}' for index in range(values.shape[1])),
                ('synopsis_features',),
                np.asarray([bool(text and text.strip()) for text in texts], dtype=bool),
            )
        )
    return tuple(blocks)


def _latent_block(name: str, values: np.ndarray) -> FeatureBlock:
    return FeatureBlock(
        name,
        name.removeprefix('synopsis-'),
        values,
        tuple(f'dimension-{index}' for index in range(values.shape[1])),
        ('synopsis_features',),
    )
