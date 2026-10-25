"""arXiv:1602.02068v2, Sec. 2, Eq. 2-4, 12; standalone operator, not full model.

Three native implementations preserve input dtype where possible. The last
axis is the probability-simplex axis. Only finite floating-point inputs are
supported; sparsemax is not differentiable at support-set changes.
"""
from __future__ import annotations

import numpy as np


def numpy_sparsemax(x: np.ndarray) -> np.ndarray:
    """Eq. 3-4 / Algorithm 1: vectorized simplex projection in O(K log K)."""
    z = np.asarray(x)
    if z.ndim < 1 or z.shape[-1] < 1 or not np.issubdtype(z.dtype, np.floating):
        raise ValueError('Expected finite floating array with a nonempty last axis')
    if not np.isfinite(z).all():
        raise ValueError('Expected finite values')
    s = np.sort(z, axis=-1)[..., ::-1]
    k = np.arange(1, z.shape[-1] + 1, dtype=z.dtype)
    partial = np.cumsum(s, axis=-1)
    support = 1.0 + k * s > partial
    count = support.sum(axis=-1, keepdims=True)
    threshold = ((s * support).sum(axis=-1, keepdims=True) - 1.0) / count
    return np.maximum(z - threshold, 0.0)


def sparsemax_bisection_reference(x: np.ndarray, iterations: int = 100) -> np.ndarray:
    """Independent numeric oracle: solve Σ max(z_i - tau,0)=1 with bisection.

    No sorting / support-index rule: designed to detect a bug in Eq. 4 coding.
    Works on small/medium float64 arrays, not designed for GPU or autodiff.
    """
    z = np.asarray(x, dtype=np.float64)
    if z.ndim < 1 or z.shape[-1] < 1 or not np.isfinite(z).all():
        raise ValueError('Expected finite values and nonempty last axis')
    lo = np.min(z, axis=-1, keepdims=True) - 2.0
    hi = np.max(z, axis=-1, keepdims=True)
    for _ in range(iterations):
        mid = (lo + hi) / 2.0
        excess = np.maximum(z - mid, 0.0).sum(axis=-1, keepdims=True)
        lo = np.where(excess > 1, mid, lo)
        hi = np.where(excess > 1, hi, mid)
    return np.maximum(z - (lo + hi) / 2.0, 0.0)


def sparsemax_jacobian_reference(x: np.ndarray) -> np.ndarray:
    """Eq. 12, one vector, for points with unchanging support only."""
    z = np.asarray(x, dtype=np.float64)
    if z.ndim != 1:
        raise ValueError('Expected a vector')
    p = numpy_sparsemax(z)
    s = (p > 0).astype(np.float64)
    return np.diag(s) - np.outer(s, s) / s.sum()


def torch_sparsemax(x):
    """Autodiff-capable, native PyTorch, differentiable off support boundaries."""
    import torch
    if not isinstance(x, torch.Tensor) or x.ndim < 1 or x.shape[-1] < 1 or not x.is_floating_point():
        raise ValueError('Expected finite floating torch.Tensor with nonempty last axis')
    if not bool(torch.isfinite(x).all()):
        raise ValueError('Expected finite values')
    ordered, _ = torch.sort(x, dim=-1, descending=True)
    indices = torch.arange(1, x.shape[-1] + 1, dtype=x.dtype, device=x.device)
    running = torch.cumsum(ordered, dim=-1)
    support = 1.0 + indices * ordered > running
    count = support.sum(dim=-1, keepdim=True)
    tau = ((ordered * support).sum(dim=-1, keepdim=True) - 1.0) / count
    return torch.clamp_min(x - tau, 0)


def tensorflow_sparsemax(x):
    """Autodiff-capable TF eager/tf.function graph with dynamic batch axes."""
    import tensorflow as tf
    z = tf.convert_to_tensor(x)
    if z.shape.rank is None or z.shape.rank < 1 or not z.dtype.is_floating:
        raise ValueError('Expected floating TensorFlow tensor with known rank >=1')
    tf.debugging.assert_positive(tf.shape(z)[-1], message='Last axis must be nonempty')
    tf.debugging.assert_all_finite(z, 'Expected finite values')
    ordered = tf.sort(z, axis=-1, direction='DESCENDING')
    count_indices = tf.cast(tf.range(1, tf.shape(z)[-1] + 1), z.dtype)
    running = tf.math.cumsum(ordered, axis=-1)
    support = 1.0 + count_indices * ordered > running
    count = tf.reduce_sum(tf.cast(support, tf.int32), axis=-1, keepdims=True)
    tau = (tf.reduce_sum(tf.where(support, ordered, tf.zeros_like(ordered)), axis=-1, keepdims=True) - 1.0) / tf.cast(count, z.dtype)
    return tf.maximum(z - tau, tf.zeros_like(z))
