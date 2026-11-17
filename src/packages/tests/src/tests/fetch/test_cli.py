from pathlib import Path
from typing import Self

import pytest

import fetch.__main__ as fetch_cli
from fetch.catalogue import FetchSummary


def _ignore_logging_setup(**_options: object) -> int:
    return 0


@pytest.mark.parametrize(
    'argv',
    [
        ['--update', '--update-ids', '1'],
        ['--update', '--force'],
        ['--update-ids', '1', '--force'],
    ],
)
def test_fetch_cli_mode_flags_are_mutually_exclusive(argv: list[str]) -> None:
    parser = fetch_cli.build_parser()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(argv)

    assert exc_info.value.code == 2


def test_fetch_cli_derives_checkpoint_from_output_and_logs_before_force_refusal(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_path = tmp_path / 'custom.json'
    derived_checkpoint = tmp_path / 'custom.checkpoint.json'
    derived_checkpoint.write_text('{}', encoding='utf-8')
    setup_calls: list[str] = []

    def _fake_setup_logging(*, level: str = 'INFO') -> int:
        setup_calls.append(level)
        return 0

    monkeypatch.setattr(fetch_cli, 'setup_logging', _fake_setup_logging)

    exit_code = fetch_cli.main(['--output', str(output_path), '--force'])

    assert exit_code == 1
    assert len(setup_calls) == 1


def test_fetch_cli_passes_derived_checkpoint_when_output_is_provided(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_path = tmp_path / 'custom.json'
    recorded_checkpoints: list[Path | None] = []

    class _FakeClient:
        last_summary: FetchSummary | None = None

        def __init__(self, *, profile: object = None) -> None:
            del profile

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *_args: object) -> None:
            pass

        def catalogue(
            self,
            _last_page: int | None = None,
            *,
            entries_path: Path,
            checkpoint_path: Path | None = None,
            overwrite: bool = False,
        ) -> list[object]:
            del entries_path, overwrite
            recorded_checkpoints.append(checkpoint_path)
            return []

    monkeypatch.setattr(fetch_cli, 'setup_logging', _ignore_logging_setup)
    monkeypatch.setattr(fetch_cli, 'TenraiClient', _FakeClient)

    exit_code = fetch_cli.main(['--output', str(output_path)])

    assert exit_code == 0
    assert recorded_checkpoints == [tmp_path / 'custom.checkpoint.json']
