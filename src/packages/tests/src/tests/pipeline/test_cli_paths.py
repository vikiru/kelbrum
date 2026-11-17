from pathlib import Path
from typing import Self

import pytest

import pipeline.__main__ as pipeline_cli
from features.config import EmbeddingSource
from fetch.errors import FetchError
from fetch.updates import UpdateResult
from pipeline.__main__ import _profile_paths
from pipeline.contracts import PipelineRunRequest
from storage.errors import StorageError


def test_default_profile_uses_generic_local_snapshot_pair() -> None:
    paths = _profile_paths('default')

    assert paths.snapshot.name == 'tenrai-anime.full.json'
    assert paths.checkpoint.name == 'tenrai-anime.full.checkpoint.json'
    assert paths.full_artifact.name == 'tenrai-anime.full.json'


def test_all_profile_uses_all_profile_snapshot_paths() -> None:
    paths = _profile_paths('all')

    assert paths.snapshot.name == 'tenrai-anime-all.json'
    assert paths.checkpoint.name == 'tenrai-anime-all.checkpoint.json'
    assert paths.full_artifact.name == 'tenrai-anime-all.full.json'
    assert isinstance(paths.snapshot, Path)


def test_pipeline_cli_update_passes_profile_and_returns_one_on_failed_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_profiles: list[str | None] = []
    ran_pipeline = False

    class _FakeClient:
        def __init__(self, *, profile: object = None) -> None:
            captured_profiles.append(getattr(profile, 'name', None))

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *_args: object) -> None:
            pass

        def update_catalogue(self, **_kwargs: object) -> UpdateResult:
            return UpdateResult(
                requested_count=1,
                new_count=0,
                updated_count=0,
                rejected_count=0,
                total_catalogue_count=0,
                failed_ids=(42,),
            )

    def _run_pipeline(_request: PipelineRunRequest) -> None:
        nonlocal ran_pipeline
        ran_pipeline = True

    monkeypatch.setattr(pipeline_cli, 'setup_logging', lambda **_kwargs: 0)
    monkeypatch.setattr(pipeline_cli, 'TenraiClient', _FakeClient)
    monkeypatch.setattr(pipeline_cli, 'run_catalogue_pipeline', _run_pipeline)

    exit_code = pipeline_cli.main(['--profile', 'sfw', '--update', '--without-embeddings'])

    assert exit_code == 1
    assert captured_profiles == ['sfw']
    assert not ran_pipeline


def test_pipeline_cli_keeps_canonical_embedding_identifier_and_passes_local_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    local_dir = tmp_path / 'sentence-transformers--all-mpnet-base-v2'
    local_dir.mkdir()
    captured_requests: list[PipelineRunRequest] = []

    class _FakeClient:
        def __init__(self, *, profile: object = None) -> None:
            del profile

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *_args: object) -> None:
            pass

    monkeypatch.setattr(pipeline_cli, 'setup_logging', lambda **_kwargs: 0)
    monkeypatch.setattr(pipeline_cli, 'TenraiClient', _FakeClient)
    monkeypatch.setattr(pipeline_cli, 'huggingface_model_path', lambda _model_id: local_dir)
    monkeypatch.setattr(pipeline_cli, 'run_catalogue_pipeline', captured_requests.append)

    exit_code = pipeline_cli.main(
        ['--profile', 'r-plus', '--embedding-model', 'sentence-transformers/all-mpnet-base-v2']
    )

    assert exit_code == 0
    assert len(captured_requests) == 1
    request = captured_requests[0]
    embedding = request.pipeline_plan.feature_config.embedding
    assert embedding is not None
    assert embedding.source is EmbeddingSource.LOCAL
    assert embedding.identifier == 'sentence-transformers/all-mpnet-base-v2'
    assert request.embedding_model_path == local_dir


@pytest.mark.parametrize(
    'error',
    [FetchError('boom'), StorageError('bad io'), OSError('disk'), ValueError('bad')],
)
def test_pipeline_cli_catches_known_errors_and_returns_one(
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
) -> None:
    class _FakeClient:
        def __init__(self, *, profile: object = None) -> None:
            del profile

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *_args: object) -> None:
            pass

    def _raise(_request: PipelineRunRequest) -> None:
        raise error

    monkeypatch.setattr(pipeline_cli, 'setup_logging', lambda **_kwargs: 0)
    monkeypatch.setattr(pipeline_cli, 'TenraiClient', _FakeClient)
    monkeypatch.setattr(pipeline_cli, 'run_catalogue_pipeline', _raise)

    assert pipeline_cli.main(['--without-embeddings']) == 1
