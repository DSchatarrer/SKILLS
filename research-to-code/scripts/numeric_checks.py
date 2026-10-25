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


@dataclass(frozen=True)
class GradientCheckResult:
    """Diagnostic evidence, not a proof of differentiability or global correctness."""

    relative_steps: tuple[float, ...]
    max_abs_errors: tuple[float, ...]
    max_scaled_errors: tuple[float, ...]
    max_step_disagreement: float


def check_gradient(
    f: Callable[[np.ndarray], float],
    x: np.ndarray,
    expected_gradient: np.ndarray,
    *,
    relative_steps: tuple[float, ...] = (1e-4, 1e-5),
    atol: float = 1e-7,
    rtol: float = 1e-5,
) -> GradientCheckResult:
    """Compare a *separately derived* scalar-function gradient with central differences.

    Checks at >=2 distinct steps and reports their disagreement. Both the analytic
    oracle and the differentiability of f at x must be justified by the caller;
    finite differences cannot establish either fact. Do not use on uncontrolled
    stochastic functions, kinks, or discontinuities.
    """
    steps = tuple(relative_steps)
    if (len(steps) < 2 or len(set(steps)) != len(steps)
            or any(not np.isfinite(h) or not (0 < h < 0.1) for h in steps)):
        raise ValueError("Se requieren al menos dos pasos distintos y finitos en (0, 0.1)")
    x64 = np.asarray(x, dtype=np.float64)
    expected = np.asarray(expected_gradient, dtype=np.float64)
    if x64.shape != expected.shape:
        raise ValueError(f"Shape del gradiente incorrecto: {expected.shape}; esperado {x64.shape}")
    if not np.all(np.isfinite(x64)) or not np.all(np.isfinite(expected)):
        raise ValueError("La entrada y el gradiente analítico deben ser finitos")
    estimates = []
    errors = []
    for h in steps:
        calculated = finite_difference_gradient(f, x64, relative_step=h)
        try:
            stats = compare_arrays(calculated, expected, atol=atol, rtol=rtol)
        except AssertionError as exc:
            raise AssertionError(f"Gradiente incorrecto para paso relativo {h}: {exc}") from exc
        estimates.append(calculated)
        errors.append(stats)
    max_step_disagreement = max(
        float(np.max(np.abs(estimates[i] - estimates[j]), initial=0))
        for i in range(len(estimates))
        for j in range(i + 1, len(estimates))
    )
    return GradientCheckResult(
        relative_steps=steps,
        max_abs_errors=tuple(e.max_abs_error for e in errors),
        max_scaled_errors=tuple(e.max_scaled_error for e in errors),
        max_step_disagreement=max_step_disagreement,
    )
