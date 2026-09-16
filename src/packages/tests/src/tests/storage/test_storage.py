from pathlib import Path

import msgspec
import pytest

from storage.errors import MissingArtifactError
from storage.hashing import sha256_file
from storage.json_io import read_json, write_json


class StoredRecord(msgspec.Struct, frozen=True):
    record_id: int
    name: str


def test_json_storage_is_deterministic_and_round_trips_typed_records(tmp_path: Path) -> None:
    path = tmp_path / 'nested' / 'record.json'
    record = StoredRecord(record_id=7, name='example')

    write_json(path, {'z': 1, 'record': record, 'a': [2, 1]})
    first_bytes = path.read_bytes()
    write_json(path, {'a': [2, 1], 'record': record, 'z': 1})

    assert path.read_bytes() == first_bytes
    decoded = read_json(path, dict[str, object])
    assert decoded['record'] == {'name': 'example', 'record_id': 7}


def test_json_storage_reports_missing_artifacts(tmp_path: Path) -> None:
    with pytest.raises(MissingArtifactError):
        read_json(tmp_path / 'missing.json', StoredRecord)


def test_sha256_file_streams_with_a_configurable_chunk_size(tmp_path: Path) -> None:
    path = tmp_path / 'payload.bin'
    path.write_bytes(b'kelbrum' * 257)

    assert sha256_file(path, chunk_size=3) == sha256_file(path)
    with pytest.raises(ValueError, match='positive'):
        sha256_file(path, chunk_size=0)
