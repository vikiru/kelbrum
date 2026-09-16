"""Command-line entry point for Tenrai catalogue fetching."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from config import (
    Settings,
    bind_logger,
    setup_logging,
    tenrai_profile_snapshot_path,
    tenrai_r_plus_checkpoint_path,
    tenrai_r_plus_snapshot_path,
)
from fetch.client import TenraiClient
from fetch.errors import FetchError
from fetch.profiles import CatalogueProfile


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for catalogue acquisition modes."""
    parser = argparse.ArgumentParser(description='Fetch Tenrai catalogue pages into a JSON snapshot.')
    parser.add_argument('--last-page', type=int, help='Last catalogue page to fetch (default: discover all pages).')
    parser.add_argument(
        '--mode',
        choices=('sfw', 'r-plus', 'all'),
        default='r-plus',
        help='Catalogue policy to use (default: r-plus).',
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help='Snapshot JSON path; defaults according to mode.',
    )
    checkpoint = parser.add_mutually_exclusive_group()
    checkpoint.add_argument('--checkpoint', type=Path, default=None, help='Checkpoint path for resumable fetching.')
    checkpoint.add_argument('--no-checkpoint', action='store_true', help='Disable resumable checkpointing.')
    parser.add_argument('--force', action='store_true', help='Replace an existing snapshot.')
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Fetch the selected Tenrai profile and return a process exit status."""
    args = build_parser().parse_args(argv)
    if args.mode == 'sfw':
        profile = CatalogueProfile.sfw(limit=50)
        default_output = tenrai_profile_snapshot_path('sfw')
        default_checkpoint = default_output.with_suffix('.checkpoint.json')
    elif args.mode == 'r-plus':
        profile = CatalogueProfile.r_plus(limit=50)
        default_output, default_checkpoint = tenrai_r_plus_snapshot_path(), tenrai_r_plus_checkpoint_path()
    else:
        profile = CatalogueProfile.all_anime(limit=50)
        default_output = tenrai_profile_snapshot_path('all')
        default_checkpoint = default_output.with_suffix('.checkpoint.json')
    output = args.output or default_output
    checkpoint_path = args.checkpoint or default_checkpoint
    if args.force and not args.no_checkpoint and checkpoint_path.is_file():
        raise SystemExit('Refusing --force with an existing checkpoint; use --no-checkpoint for a fresh fetch.')
    setup_logging(level=Settings().log_level)
    log = bind_logger(package='fetch', stage='fetch')
    log.info('Starting fetch [{}].', args.mode.upper())
    try:
        with TenraiClient(profile=profile) as client:
            entries = client.catalogue(
                args.last_page,
                entries_path=output,
                checkpoint_path=None if args.no_checkpoint else checkpoint_path,
                overwrite=args.force,
            )
            summary = client.last_summary
    except (FetchError, OSError, ValueError) as error:
        log.log('ERROR', 'Fetch failed: {}', error)
        return 1
    if summary is None:
        log.info('Completed fetch: {} entries written to {}.', len(entries), output)
    else:
        log.info('Completed fetch: {} entries written to {} in {:.2f}s.', len(entries), output, summary.total_seconds)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
