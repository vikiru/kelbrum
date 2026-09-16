"""Small array-first normalization strategies."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from enum import StrEnum
from typing import Self, override

import msgspec
import numpy as np
import orjson
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
_MATRIX_DIMENSIONS = 2


class TransformName(StrEnum):
    """Supported fitted numeric transformation steps."""

    LOG1P = 'log1p'
    MINMAX = 'minmax'
    STANDARD = 'standard'
    ROBUST = 'robust'
    MAXABS = 'maxabs'


class FittedState(msgspec.Struct, frozen=True):
    strategy: str
    source_name: str
    parameters: tuple[float, ...]

    def to_json(self) -> bytes:
        """Serialize fitted parameters as compact deterministic JSON."""
        return orjson.dumps(msgspec.to_builtins(self), option=orjson.OPT_SORT_KEYS)

    @classmethod
    def from_json(cls, payload: bytes) -> 'FittedState':
        return msgspec.convert(orjson.loads(payload), type=cls)


class BaseScaler(ABC):
    """Common fitted-state lifecycle for numeric scaling strategies."""

    def __init__(self, *, source_name: str = 'value') -> None:
        self.source_name = source_name
        self.state: FittedState | None = None

    @abstractmethod
    def fit(self, values: FloatArray) -> Self:
        """Fit this strategy to numeric values."""

    @abstractmethod
    def transform(self, values: FloatArray) -> FloatArray:
        """Transform values using the fitted strategy."""

    def fit_transform(self, values: FloatArray) -> FloatArray:
        """Fit this strategy and transform the same values."""
        return self.fit(values).transform(values)

    def _require_state(self) -> FittedState:
        if self.state is None:
            raise RuntimeError(f'{type(self).__name__} must be fitted before transform')
        return self.state


class TransformDefinition(msgspec.Struct, frozen=True):
    """Describe one normalization transform and its implementation."""

    identity: str
    scaler_type: type[BaseScaler] | None = None
    function: Callable[[FloatArray], FloatArray] | None = None

    def __post_init__(self) -> None:
        if (self.scaler_type is None) == (self.function is None):
            raise ValueError('transform definition requires exactly one implementation')


class MinMaxScaler(BaseScaler):
    """Fit a deterministic min-max transform column-wise."""

    @override
    def fit(self, values: FloatArray) -> 'MinMaxScaler':
        array = _validate(values)
        minimum = np.nanmin(array, axis=0)
        maximum = np.nanmax(array, axis=0)
        self.state = FittedState('minmax', self.source_name, _python_floats(np.r_[minimum, maximum]))
        return self

    @override
    def transform(self, values: FloatArray) -> FloatArray:
        state = self._require_state()
        array = _validate(values)
        width = len(state.parameters) // 2
        minimum = np.asarray(state.parameters[:width])
        scale = np.asarray(state.parameters[width:]) - minimum
        scale = np.where(scale == 0, 1.0, scale)
        return ((array - minimum) / scale).astype(np.float64, copy=False)


class RobustScaler(BaseScaler):
    """Scale values by their median and interquartile range."""

    @override
    def fit(self, values: FloatArray) -> 'RobustScaler':
        array = _validate(values)
        median = np.median(array, axis=0)
        q1, q3 = np.percentile(array, [25, 75], axis=0)
        self.state = FittedState('robust', self.source_name, _python_floats(np.r_[median, q1, q3]))
        return self

    @override
    def transform(self, values: FloatArray) -> FloatArray:
        state = self._require_state()
        array = _validate(values)
        width = len(state.parameters) // 3
        median = np.asarray(state.parameters[:width])
        q1 = np.asarray(state.parameters[width : 2 * width])
        q3 = np.asarray(state.parameters[2 * width :])
        scale = np.where(q3 == q1, 1.0, q3 - q1)
        return ((array - median) / scale).astype(np.float64, copy=False)


class StandardScaler(BaseScaler):
    """Center values and scale them by population standard deviation."""

    @override
    def fit(self, values: FloatArray) -> 'StandardScaler':
        array = _validate(values)
        mean = np.mean(array, axis=0)
        standard_deviation = np.std(array, axis=0)
        scale = np.where(standard_deviation == 0, 1.0, standard_deviation)
        self.state = FittedState('standard', self.source_name, _python_floats(np.r_[mean, scale]))
        return self

    @override
    def transform(self, values: FloatArray) -> FloatArray:
        state = self._require_state()
        array = _validate(values)
        width = len(state.parameters) // 2
        return ((array - np.asarray(state.parameters[:width])) / np.asarray(state.parameters[width:])).astype(
            np.float64, copy=False
        )


class MaxAbsScaler(BaseScaler):
    """Scale each column by its largest absolute value."""

    @override
    def fit(self, values: FloatArray) -> 'MaxAbsScaler':
        array = _validate(values)
        scale = np.max(np.abs(array), axis=0)
        self.state = FittedState('maxabs', self.source_name, _python_floats(np.where(scale == 0, 1.0, scale)))
        return self

    @override
    def transform(self, values: FloatArray) -> FloatArray:
        state = self._require_state()
        return (_validate(values) / np.asarray(state.parameters)).astype(np.float64, copy=False)


def log1p(values: FloatArray) -> FloatArray:
    """Apply a finite, non-negative log1p transform."""
    array = _validate(values)
    if (array < 0).any():
        raise ValueError('log1p input must be non-negative')
    return np.log1p(array)


Scaler = BaseScaler


def restore(state: FittedState) -> Scaler:
    """Restore a fitted scaler from its typed, serialized state."""
    definition = _transform_definition(state.strategy)
    if definition.scaler_type is None:
        raise ValueError(f'transform state cannot restore non-fitted transform: {state.strategy}')
    scaler_type = definition.scaler_type
    scaler = scaler_type(source_name=state.source_name)
    scaler.state = state
    return scaler


def transform(values: FloatArray, steps: Sequence[str | TransformName]) -> FloatArray:
    """Apply a validated property-specific transformation pipeline."""
    result = _validate(values)
    for step in steps:
        definition = _transform_definition(step)
        if definition.function is not None:
            result = definition.function(result)
        else:
            scaler_type = definition.scaler_type
            if scaler_type is None:
                raise RuntimeError(f'transform definition has no implementation: {step}')
            result = scaler_type().fit_transform(result)
    return result


def transform_identity(name: str | TransformName) -> str:
    """Return the implementation identity for one normalization transform."""
    return _transform_definition(name).identity


def _transform_definition(name: str | TransformName) -> TransformDefinition:
    try:
        return TRANSFORM_REGISTRY[TransformName(name)]
    except (KeyError, ValueError) as error:
        raise ValueError(f'unsupported numeric transform: {name}') from error


def _validate(values: FloatArray) -> FloatArray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim not in {1, 2}:
        raise ValueError(f'expected a one- or two-dimensional array, got {array.ndim} dimensions')
    if array.size == 0:
        raise ValueError('normalization input must not be empty')
    if not np.isfinite(array).all():
        raise ValueError('normalization input must contain only finite values')
    return array if array.ndim == _MATRIX_DIMENSIONS else array.reshape(-1, 1)


def _python_floats(values: np.ndarray) -> tuple[float, ...]:
    return tuple(float(value) for value in values.ravel())


TRANSFORM_REGISTRY: dict[TransformName, TransformDefinition] = {
    TransformName.LOG1P: TransformDefinition('log1p-v1', function=log1p),
    TransformName.MINMAX: TransformDefinition('minmax-v1', scaler_type=MinMaxScaler),
    TransformName.STANDARD: TransformDefinition('standard-v1', scaler_type=StandardScaler),
    TransformName.ROBUST: TransformDefinition('robust-v1', scaler_type=RobustScaler),
    TransformName.MAXABS: TransformDefinition('maxabs-v1', scaler_type=MaxAbsScaler),
}
