"""Implementation of the bundled local specification, without external provider IDs."""
from __future__ import annotations
import numpy as np


def _inputs(values, weights):
    x=np.asarray(values, dtype=np.float64)
    p=np.asarray(weights, dtype=np.float64)
    if x.ndim != 1 or p.ndim != 1 or x.shape != p.shape or x.size == 0:
        raise ValueError("values and weights must be nonempty, equally-sized vectors")
    if not np.isfinite(x).all() or not np.isfinite(p).all():
        raise ValueError("values and weights must be finite")
    if np.any(p < 0) or not np.isclose(float(np.sum(p)), 1.0, rtol=0, atol=1e-12):
        raise ValueError("weights must be nonnegative and sum to one")
    return x,p


def weighted_expectation_reference(values, weights) -> float:
    x,p=_inputs(values, weights)
    total=0.0
    for i in range(len(x)):
        total += float(p[i])*float(x[i])
    return total


def weighted_expectation(values, weights) -> float:
    x,p=_inputs(values, weights)
    return float(np.dot(x,p))
