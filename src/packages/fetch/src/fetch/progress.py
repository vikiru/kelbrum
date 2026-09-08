"""Rich progress display for sequential fetches."""

from contextlib import AbstractContextManager
from typing import Self, override

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


class FetchProgress(AbstractContextManager['FetchProgress']):
    def __init__(self, total: int) -> None:
        if total < 1:
            raise ValueError('progress total must be positive')
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn('[progress.description]{task.description}'),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        )
        self._total_pages = total
        self._task_id = self._progress.add_task('Fetching Tenrai catalogue', total=total)

    @override
    def __enter__(self) -> Self:
        self._progress.start()
        return self

    def advance(self) -> None:
        self._progress.advance(self._task_id)

    def complete(self, pages: int) -> None:
        self._progress.update(self._task_id, completed=pages)

    def update(self, *, page: int, anime_count: int, total_anime: int) -> None:
        self._progress.update(
            self._task_id,
            description=(f'Page {page}/{self._total_pages} • {anime_count:,}/{total_anime:,} anime'),
        )

    @override
    def __exit__(self, *args: object) -> None:
        self._progress.stop()
