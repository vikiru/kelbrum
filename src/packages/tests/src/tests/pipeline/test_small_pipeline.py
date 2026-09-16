from collections.abc import Sequence
from pathlib import Path

from features.config import FeatureConfig
from fetch.contracts import TenraiAnimeEntry
from fetch.filters import CatalogueFilters
from pipeline.contracts import CatalogueProfilePaths, PipelineRunRequest
from pipeline.plan import PipelinePlan
from pipeline.run import _processed_cache_matches, run_catalogue_pipeline
from processing.eligibility import EligibilityPolicy
from recommender.contracts import RecommendationConfig
from storage.json_io import read_json, write_json


class FakePipelineClient:
    def __init__(self, entries: Sequence[TenraiAnimeEntry]) -> None:
        self.entries = list(entries)

    def catalogue(
        self,
        *,
        filters: CatalogueFilters,
        checkpoint_path: Path,
        entries_path: Path,
        overwrite: bool,
    ) -> list[TenraiAnimeEntry]:
        del filters, checkpoint_path, overwrite
        write_json(entries_path, self.entries)
        return self.entries

    def enrich(
        self,
        anime_ids: Sequence[int],
        output_path: Path,
        *,
        overwrite: bool,
        profile: str | None,
    ) -> Sequence[TenraiAnimeEntry]:
        del anime_ids, overwrite, profile
        write_json(output_path, self.entries)
        return self.entries


def _entry(anime_id: int, title: str) -> TenraiAnimeEntry:
    return TenraiAnimeEntry(
        mal_id=anime_id,
        title=title,
        type='TV',
        rating='PG',
        episodes=12,
        duration='24 min per ep',
        year=2024,
        status='Finished Airing',
        score=8.0,
        synopsis=f'{title} is a quiet forest adventure.',
        genres=[],
        themes=[],
        demographics=[],
    )


def test_small_pipeline_runs_from_fake_client_to_temporary_export(tmp_path: Path) -> None:
    entries = (_entry(1, 'One'), _entry(2, 'Two'))
    source_dir = tmp_path / 'source'
    output_dir = tmp_path / 'output'
    frontend_dir = tmp_path / 'frontend'
    source_dir.mkdir()
    client = FakePipelineClient(entries)
    paths = CatalogueProfilePaths(
        snapshot=source_dir / 'snapshot.json',
        checkpoint=source_dir / 'checkpoint.json',
        full_artifact=source_dir / 'full.json',
        filters=CatalogueFilters.all_anime(),
    )

    request = PipelineRunRequest(
        client=client,
        profile='fixture',
        profile_paths=paths,
        pipeline_plan=PipelinePlan(feature_config=FeatureConfig(synopsis_min_df=1, synopsis_max_df=1.0)),
        recommendation_config=RecommendationConfig(limit=1),
        output_dir=output_dir,
        frontend_output_dir=frontend_dir,
        embedding_cache=None,
        relationship_graph_path=tmp_path / 'relationship-graph.json',
        recommendation_path=tmp_path / 'recommendations',
        processing_policy=EligibilityPolicy(require_primary_image=False),
        recommendation_batch_size=50,
    )
    run = run_catalogue_pipeline(request)

    assert run.manifest.anime_count == 2
    assert tuple(run.features.anime_ids.tolist()) == (1, 2)
    assert (output_dir / 'canonical.parquet').is_file()
    assert (frontend_dir / 'artifact-manifest.json').is_file()
    assert (tmp_path / 'relationship-graph.json').is_file()
    first_manifest = read_json(frontend_dir / 'artifact-manifest.json', dict[str, object])
    first_graph = read_json(tmp_path / 'relationship-graph.json', dict[str, object])
    first_chunks = read_json(tmp_path / 'recommendations' / 'chunk-0000.json', dict[str, list[int]])
    first_chunk_bytes = (tmp_path / 'recommendations' / 'chunk-0000.json').read_bytes()
    assert set(first_chunks) == {'1', '2'}
    files = first_manifest['files']
    assert isinstance(files, list)
    manifest_files = {item['path'] for item in files if isinstance(item, dict) and isinstance(item.get('path'), str)}
    assert {'homepage.json', 'top-100.json'} <= manifest_files

    run_again = run_catalogue_pipeline(request)

    assert run_again.manifest.anime_count == run.manifest.anime_count
    assert run_again.manifest.feature_block_names == run.manifest.feature_block_names
    assert run_again.manifest.schema_version == run.manifest.schema_version
    assert (
        read_json(frontend_dir / 'artifact-manifest.json', dict[str, object])['build_identity']
        == first_manifest['build_identity']
    )
    assert (
        read_json(tmp_path / 'relationship-graph.json', dict[str, object])['build_identity']
        == first_graph['build_identity']
    )
    assert (tmp_path / 'recommendations' / 'chunk-0000.json').read_bytes() == first_chunk_bytes


def test_corrupt_processing_audit_is_treated_as_a_cache_miss(tmp_path: Path) -> None:
    source_path = tmp_path / 'snapshot.json'
    audit_path = tmp_path / 'processing-audit.json'
    write_json(source_path, ())
    audit_path.write_text('{corrupt', encoding='utf-8')

    assert not _processed_cache_matches(audit_path, source_path, EligibilityPolicy())
