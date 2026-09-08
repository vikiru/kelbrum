"""Small array-first normalization strategies."""

from collections.abc import Sequence

import msgspec
import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
_MATRIX_DIMENSIONS = 2


class FittedState(msgspec.Struct, frozen=True):
    strategy: str
    source_name: str
    parameters: tuple[float, ...]

    def to_json(self) -> bytes:
        """Serialize fitted parameters as compact deterministic JSON."""
        return msgspec.json.encode(self)

    @classmethod
    def from_json(cls, payload: bytes) -> 'FittedState':
        return msgspec.json.decode(payload, type=cls)


class MinMaxScaler:
    """Fit a deterministic min-max transform column-wise."""

    def __init__(self, *, source_name: str = 'value') -> None:
        self.source_name = source_name
        self.state: FittedState | None = None

    def fit(self, values: FloatArray) -> 'MinMaxScaler':
        array = _validate(values)
        minimum = np.nanmin(array, axis=0)
        maximum = np.nanmax(array, axis=0)
        self.state = FittedState('minmax', self.source_name, _python_floats(np.r_[minimum, maximum]))
        return self

    def transform(self, values: FloatArray) -> FloatArray:
        if self.state is None:
            raise RuntimeError('MinMaxScaler must be fitted before transform')
        array = _validate(values)
        width = len(self.state.parameters) // 2
        minimum = np.asarray(self.state.parameters[:width])
        scale = np.asarray(self.state.parameters[width:]) - minimum
        scale = np.where(scale == 0, 1.0, scale)
        return ((array - minimum) / scale).astype(np.float64, copy=False)

    def fit_transform(self, values: FloatArray) -> FloatArray:
        return self.fit(values).transform(values)


class RobustScaler:
    """Scale values by their median and interquartile range."""

    def __init__(self, *, source_name: str = 'value') -> None:
        self.source_name = source_name
        self.state: FittedState | None = None

    def fit(self, values: FloatArray) -> 'RobustScaler':
        array = _validate(values)
        median = np.median(array, axis=0)
        q1, q3 = np.percentile(array, [25, 75], axis=0)
        self.state = FittedState('robust', self.source_name, _python_floats(np.r_[median, q1, q3]))
        return self

    def transform(self, values: FloatArray) -> FloatArray:
        if self.state is None:
            raise RuntimeError('RobustScaler must be fitted before transform')
        array = _validate(values)
        width = len(self.state.parameters) // 3
        median = np.asarray(self.state.parameters[:width])
        q1 = np.asarray(self.state.parameters[width : 2 * width])
        q3 = np.asarray(self.state.parameters[2 * width :])
        scale = np.where(q3 == q1, 1.0, q3 - q1)
        return ((array - median) / scale).astype(np.float64, copy=False)

    def fit_transform(self, values: FloatArray) -> FloatArray:
        return self.fit(values).transform(values)


class StandardScaler:
    """Center values and scale them by population standard deviation."""

    def __init__(self, *, source_name: str = 'value') -> None:
        self.source_name = source_name
        self.state: FittedState | None = None

    def fit(self, values: FloatArray) -> 'StandardScaler':
        array = _validate(values)
        mean = np.mean(array, axis=0)
        standard_deviation = np.std(array, axis=0)
        scale = np.where(standard_deviation == 0, 1.0, standard_deviation)
        self.state = FittedState('standard', self.source_name, _python_floats(np.r_[mean, scale]))
        return self

    def transform(self, values: FloatArray) -> FloatArray:
        if self.state is None:
            raise RuntimeError('StandardScaler must be fitted before transform')
        array = _validate(values)
        width = len(self.state.parameters) // 2
        return ((array - np.asarray(self.state.parameters[:width])) / np.asarray(self.state.parameters[width:])).astype(
            np.float64, copy=False
        )

    def fit_transform(self, values: FloatArray) -> FloatArray:
        return self.fit(values).transform(values)


class MaxAbsScaler:
    """Scale each column by its largest absolute value."""

    def __init__(self, *, source_name: str = 'value') -> None:
        self.source_name = source_name
        self.state: FittedState | None = None

    def fit(self, values: FloatArray) -> 'MaxAbsScaler':
        array = _validate(values)
        scale = np.max(np.abs(array), axis=0)
        self.state = FittedState('maxabs', self.source_name, _python_floats(np.where(scale == 0, 1.0, scale)))
        return self

    def transform(self, values: FloatArray) -> FloatArray:
        if self.state is None:
            raise RuntimeError('MaxAbsScaler must be fitted before transform')
        return (_validate(values) / np.asarray(self.state.parameters)).astype(np.float64, copy=False)

    def fit_transform(self, values: FloatArray) -> FloatArray:
        return self.fit(values).transform(values)


def log1p(values: FloatArray) -> FloatArray:
    """Apply a finite, non-negative log1p transform."""
    array = _validate(values)
    if (array < 0).any():
        raise ValueError('log1p input must be non-negative')
    return np.log1p(array)


def transform(values: FloatArray, steps: Sequence[str]) -> FloatArray:
    """Apply a validated property-specific transformation pipeline."""
    result = _validate(values)
    for step in steps:
        if step == 'log1p':
            result = log1p(result)
            continue
        scaler_type = {
            'minmax': MinMaxScaler,
            'standard': StandardScaler,
            'robust': RobustScaler,
            'maxabs': MaxAbsScaler,
        }.get(step)
        if scaler_type is None:
            raise ValueError(f'unsupported numeric transform: {step}')
        result = scaler_type().fit_transform(result)
    return result


def _validate(values: FloatArray) -> FloatArray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim not in {1, 2}:
        raise ValueError(f'expected a one- or two-dimensional array, got {array.ndim} dimensions')
    if not np.isfinite(array).all():
        raise ValueError('normalization input must contain only finite values')
    return array if array.ndim == _MATRIX_DIMENSIONS else array.reshape(-1, 1)


def _python_floats(values: np.ndarray) -> tuple[float, ...]:
    return tuple(float(value) for value in values.ravel())
