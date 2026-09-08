"""Row-aligned categorical features shared by retrieval and scoring."""

from collections.abc import Mapping, Sequence

import msgspec

from anime_catalogue import AnimeCatalogue


class CategoricalFeatureStore(msgspec.Struct, frozen=True):
    """Immutable categorical feature view aligned to one catalogue row order."""

    anime_ids: tuple[int, ...]
    genres: tuple[tuple[str, ...], ...]
    themes: tuple[tuple[str, ...], ...]
    demographics: tuple[tuple[str, ...], ...]
    tags: tuple[tuple[str, ...], ...]

    def __post_init__(self) -> None:
        row_count = len(self.anime_ids)
        if len(set(self.anime_ids)) != row_count:
            raise ValueError('categorical feature IDs must be unique')
        if any(len(values) != row_count for values in (self.genres, self.themes, self.demographics, self.tags)):
            raise ValueError('categorical features must preserve anime-ID alignment')

    @classmethod
    def from_catalogue(cls, catalogue: AnimeCatalogue, tags: Mapping[int, Sequence[str]]) -> 'CategoricalFeatureStore':
        """Build categorical features from catalogue facts and derived tag values."""
        return cls(
            anime_ids=catalogue.anime_ids,
            genres=catalogue.genres,
            themes=catalogue.themes,
            demographics=catalogue.demographics,
            tags=tuple(tuple(tags.get(anime_id, ())) for anime_id in catalogue.anime_ids),
        )

    def mappings(self) -> dict[str, dict[int, tuple[str, ...]]]:
        """Return ID-keyed projections for legacy scorers and diagnostic tools."""
        return {
            name: dict(zip(self.anime_ids, values, strict=True))
            for name, values in (
                ('genres', self.genres),
                ('themes', self.themes),
                ('demographics', self.demographics),
                ('tags', self.tags),
            )
        }
