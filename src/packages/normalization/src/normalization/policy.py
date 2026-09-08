"""Explicit missing-value policies for numeric feature inputs."""

from enum import StrEnum

import numpy as np
from numpy.typing import NDArray


class MissingPolicy(StrEnum):
    PRESERVE = 'preserve'
    MEDIAN = 'median'
    ZERO = 'zero'
    REJECT = 'reject'


def apply_missing_policy(values: NDArray[np.float64], policy: MissingPolicy) -> NDArray[np.float64]:
    """Apply a declared policy to NaN values without changing finite values."""
    array = np.asarray(values, dtype=np.float64).copy()
    if policy is MissingPolicy.REJECT and np.isnan(array).any():
        raise ValueError('numeric input contains missing values')
    if policy is MissingPolicy.MEDIAN:
        medians = np.nanmedian(array, axis=0)
        if array.ndim == 1:
            median = float(medians) if np.isfinite(medians) else 0.0
            array[np.isnan(array)] = median
        else:
            rows, columns = np.where(np.isnan(array))
            replacement = np.where(np.isfinite(medians), medians, 0.0)
            array[rows, columns] = replacement[columns]
    elif policy is MissingPolicy.ZERO:
        array[np.isnan(array)] = 0.0
    return array
