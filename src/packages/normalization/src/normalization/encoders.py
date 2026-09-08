"""Reusable categorical and bucket normalization transforms."""

import math
from collections.abc import Iterable, Sequence

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder


def one_hot(values: Sequence[str | None]) -> tuple[csr_matrix, tuple[str, ...]]:
    """Encode one categorical value per row with stable unknown handling."""
    if not values:
        return csr_matrix((0, 0), dtype=np.float32), ()
    clean = np.asarray([_clean_value(value) for value in values], dtype=object).reshape(-1, 1)
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=True, dtype=np.float32)
    matrix = encoder.fit_transform(clean)
    names = tuple(str(name) for name in np.asarray(encoder.categories_[0]).tolist())
    return csr_matrix(matrix), names


def multi_hot(values: Iterable[Iterable[str | None] | None]) -> tuple[csr_matrix, tuple[str, ...]]:
    """Encode deterministic set membership as a sparse binary matrix."""
    rows = [clean_labels(row) for row in values]
    encoder = MultiLabelBinarizer(sparse_output=True)
    matrix = csr_matrix(encoder.fit_transform(rows), dtype=np.float32)
    return matrix, tuple(str(name) for name in encoder.classes_)


def clean_labels(values: Iterable[str | None] | None) -> tuple[str, ...]:
    """Normalize optional list-valued categorical fields."""
    if values is None:
        return ()
    return tuple(sorted({value.strip() for value in values if value and value.strip()}))


def bucketize(
    values: Sequence[float | None], *, boundaries: tuple[float, ...], missing_below: float
) -> tuple[csr_matrix, tuple[str, ...]]:
    """Encode values into deterministic inclusive-lower-bound buckets."""
    if not boundaries or tuple(sorted(boundaries)) != boundaries:
        raise ValueError('bucket boundaries must be sorted and non-empty')
    labels = (
        'missing',
        *(
            f'{start}-{boundaries[index + 1] - 1}' if index + 1 < len(boundaries) else f'{start}+'
            for index, start in enumerate(boundaries)
        ),
    )
    col_indices: list[int] = []
    for value in values:
        if value is None or not math.isfinite(value) or value < missing_below:
            col_indices.append(0)
            continue
        index = max(index for index, start in enumerate(boundaries) if value >= start)
        col_indices.append(index + 1)
    n_rows = len(col_indices)
    row_indices = np.arange(n_rows, dtype=np.int32)
    cols = np.asarray(col_indices, dtype=np.int32)
    data = np.ones(n_rows, dtype=np.float32)
    matrix = csr_matrix((data, (row_indices, cols)), shape=(n_rows, len(labels)), dtype=np.float32)
    return matrix, labels


def _clean_value(value: str | None) -> str:
    if not value or value.strip().lower() in {'unknown', 'n/a', 'not available'}:
        return ''
    return value.strip()
