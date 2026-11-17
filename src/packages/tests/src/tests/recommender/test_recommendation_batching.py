from collections.abc import Mapping, Sequence

import pytest

from recommender.contracts import RawRecommendation
from recommender.pipeline import Recommender
from recommender.surfacing import SurfacingPolicy


def test_recommend_ids_many_processes_bounded_batches_and_releases_pairwise_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recommender = object.__new__(Recommender)
    recommender._relationship_index = None
    recommender._surfacing_policy = SurfacingPolicy()
    recommender._pairwise_dense_cosine_cache = {}
    batch_ids: list[tuple[int, ...]] = []
    cache_sizes_at_batch_start: list[int] = []

    def raw_recommend_many(source_ids: Sequence[int]) -> Mapping[int, tuple[RawRecommendation, ...]]:
        cache_sizes_at_batch_start.append(len(recommender._pairwise_dense_cosine_cache))
        batch_ids.append(tuple(source_ids))
        recommender._pairwise_dense_cosine_cache[(source_ids[0], source_ids[0])] = 1.0
        return {source_id: (RawRecommendation(source_id, source_id, 1.0, (), True, True),) for source_id in source_ids}

    monkeypatch.setattr(recommender, 'raw_recommend_many', raw_recommend_many)

    recommendations = recommender.recommend_ids_many((1, 2, 3, 4, 5), limit=10, source_batch_size=2)

    assert batch_ids == [(1, 2), (3, 4), (5,)]
    assert cache_sizes_at_batch_start == [0, 0, 0]
    assert recommendations == {anime_id: (anime_id,) for anime_id in range(1, 6)}
    assert recommender._pairwise_dense_cosine_cache == {(5, 5): 1.0}


def test_recommend_ids_many_rejects_non_positive_source_batch_size() -> None:
    recommender = object.__new__(Recommender)

    with pytest.raises(ValueError, match='source_batch_size must be positive'):
        recommender.recommend_ids_many((), limit=10, source_batch_size=0)
