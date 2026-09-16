"""Feature-family ablation helpers."""

from collections.abc import Iterable

import polars as pl
from msgspec.structs import replace

from features.assemble import FeatureAssemblyRequest, assemble_features
from features.blocks import FeatureBundle
from features.config import FeatureConfig


def ablate(frame: pl.DataFrame, *, config: FeatureConfig, disabled: Iterable[str] = ()) -> FeatureBundle:
    """Assemble a bundle with selected optional feature families disabled."""
    disabled_families = frozenset(disabled)
    supported = {
        'anime_type',
        'source',
        'genres',
        'themes',
        'studios',
        'episodes-bucket',
        'year-bucket',
        'numeric',
        'synopsis-tfidf',
        'synopsis-embedding',
        'rating',
        'demographics',
    }
    unknown = disabled_families - supported
    if unknown:
        raise ValueError(f'unsupported ablation families: {", ".join(sorted(unknown))}')
    active = replace(
        config,
        include_studios=config.include_studios and 'studios' not in disabled_families,
        embedding=(None if 'synopsis-embedding' in disabled_families else config.embedding),
    )
    bundle = assemble_features(frame, FeatureAssemblyRequest(config=active))
    return FeatureBundle(
        bundle.anime_ids, tuple(block for block in bundle.blocks if block.name not in disabled_families)
    )
