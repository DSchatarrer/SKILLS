"""Pedagogic mini-examples: math notation translated into *checked* NumPy code."""
from __future__ import annotations

import numpy as np


def indexed_sum_loops(a: np.ndarray, x: np.ndarray) -> np.ndarray:
    """y_i = sum_j A_ij x_j, i free and j reduced."""
    a, x = np.asarray(a), np.asarray(x)
    if a.ndim != 2 or x.ndim != 1 or a.shape[1] != x.size:
        raise ValueError("Expected A:(n,m) and x:(m,)")
    return np.array([sum(a[i, j] * x[j] for j in range(a.shape[1])) for i in range(a.shape[0])])


def indexed_sum_vectorized(a: np.ndarray, x: np.ndarray) -> np.ndarray:
    a, x = np.asarray(a), np.asarray(x)
    if a.ndim != 2 or x.ndim != 1 or a.shape[1] != x.size:
        raise ValueError("Expected A:(n,m) and x:(m,)")
    return np.einsum("ij,j->i", a, x)


def weighted_expectation(x: np.ndarray, p: np.ndarray) -> float:
    """E_p[X]=sum_i p_i*x_i for a finite discrete random variable."""
    x, p = np.asarray(x, dtype=float), np.asarray(p, dtype=float)
    if x.ndim != 1 or p.shape != x.shape or x.size == 0:
        raise ValueError("Expected nonempty x,p with identical 1D shapes")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(p)):
        raise ValueError("Non-finite input")
    if np.any(p < 0) or not np.isclose(p.sum(), 1., atol=1e-12, rtol=1e-12):
        raise ValueError("p must be nonnegative and sum to one")
    return float(np.dot(p, x))


def linear_recurrence(a: np.ndarray, b: np.ndarray, x: np.ndarray, h0: np.ndarray) -> np.ndarray:
    """h_{t+1}=A h_t+B x_t; returns all states including h_0.

    A:(d,d), B:(d,m), x:(T,m), h0:(d,), result:(T+1,d).
    """
    a, b, x, h0 = [np.asarray(i, dtype=float) for i in (a, b, x, h0)]
    if a.ndim != 2 or a.shape[0] != a.shape[1] or b.ndim != 2 or x.ndim != 2 or h0.ndim != 1:
        raise ValueError("Invalid dimensions")
    d = a.shape[0]
    if b.shape[0] != d or b.shape[1] != x.shape[1] or h0.shape != (d,):
        raise ValueError("Incompatible shapes")
    states = [h0.copy()]
    for t in range(x.shape[0]):
        states.append(a @ states[-1] + b @ x[t])
    return np.stack(states)
