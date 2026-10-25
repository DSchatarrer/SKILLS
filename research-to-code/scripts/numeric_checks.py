#!/usr/bin/env python3
"""Small CPU-only, deterministic numerical verification utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class ErrorStats:
    max_abs_error: float
    max_scaled_error: float
    n_elements: int


def compare_arrays(actual: np.ndarray, reference: np.ndarray,
                   *, atol: float = 1e-9, rtol: float = 1e-7) -> ErrorStats:
    """Validate both shape and elements; fail on NaN/Inf and excessive deviations.

    `max_scaled_error` is |a-b|/(atol+rtol*|reference|), except that exactly
    equal elements with zero denominator have scaled error 0.
    """
    if not (np.isfinite(atol) and np.isfinite(rtol) and atol >= 0 and rtol >= 0):
        raise ValueError("atol y rtol deben ser finitos y no negativos")
    a, b = np.asarray(actual), np.asarray(reference)
    if a.shape != b.shape:
        raise AssertionError(f"Shape distinto: actual {a.shape}, esperado {b.shape}")
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise AssertionError("Entradas no finitas (NaN/Inf) para comparación")
    diff = np.abs(a - b)
    threshold = atol + rtol * np.abs(b)
    scaled = np.divide(diff, threshold, out=np.zeros_like(diff, dtype=float), where=threshold != 0)
    if np.any((threshold == 0) & (diff != 0)):
        scaled = np.where((threshold == 0) & (diff != 0), np.inf, scaled)
    stats = ErrorStats(float(np.max(diff, initial=0)), float(np.max(scaled, initial=0)), a.size)
    if np.any(diff > threshold):
        raise AssertionError(f"Valores distintos: {stats}; tolerancias: atol={atol}, rtol={rtol}")
    return stats


def finite_difference_gradient(f: Callable[[np.ndarray], float], x: np.ndarray,
                               *, relative_step: float | None = None) -> np.ndarray:
    """Central differences for *smooth scalar* functions; float64 only.

    Only an approximate oracle; poor near kinks/discontinuities.
    """
    value = np.array(x, dtype=np.float64, copy=True)
    if not np.all(np.isfinite(value)):
        raise ValueError("x debe contener valores finitos")
    if relative_step is None:
        relative_step = float(np.finfo(np.float64).eps ** (1.0 / 3.0))
    if not (0 < relative_step < 0.1):
        raise ValueError("relative_step debe estar en (0, 0.1)")
    grad = np.empty_like(value)
    for index in np.ndindex(value.shape):
        delta = relative_step * max(1.0, abs(float(value[index])))
        left, right = value.copy(), value.copy()
        left[index] -= delta
        right[index] += delta
        fx_right = float(f(right))
        fx_left = float(f(left))
        if not (np.isfinite(fx_right) and np.isfinite(fx_left)):
            raise ValueError("La función no es finita alrededor del punto")
        grad[index] = (fx_right - fx_left) / (2 * delta)
    return grad
