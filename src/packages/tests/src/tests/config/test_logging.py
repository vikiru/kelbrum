from io import StringIO

import pytest
from loguru import logger

from config import LogEvent, bind_logger, emit_event, timed_event


def test_structured_event_contains_bounded_stage_metadata() -> None:
    output = StringIO()
    sink_id = logger.add(output, format='{extra}')
    try:
        emit_event(
            bind_logger(package='config', stage='test', run_id='run-1'),
            LogEvent(
                event_name='stage.completed',
                package='config',
                stage='test',
                run_id='run-1',
                entry_point='pytest',
                duration_ms=1.5,
                row_count=2,
                cache_decision='built',
                memory_mb=12.5,
                artifact_bytes=256,
            ),
        )
    finally:
        logger.remove(sink_id)

    assert 'stage.completed' in output.getvalue()
    assert 'run-1' in output.getvalue()
    assert '12.5' in output.getvalue()
    assert '256' in output.getvalue()


def test_timed_event_reports_success_and_failure_without_record_payloads() -> None:
    output = StringIO()
    sink_id = logger.add(output, format='{extra}')
    try:
        with timed_event(
            bind_logger(package='config'),
            event_name='stage.completed',
            package='config',
            stage='test',
        ):
            pass
        with (
            pytest.raises(RuntimeError, match='expected'),
            timed_event(bind_logger(package='config'), event_name='stage.completed', package='config', stage='test'),
        ):
            raise RuntimeError('expected')
    finally:
        logger.remove(sink_id)

    assert output.getvalue().count('stage.completed') == 2
    assert 'RuntimeError' in output.getvalue()
