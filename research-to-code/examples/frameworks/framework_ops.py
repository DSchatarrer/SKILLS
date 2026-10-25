"""Reference demonstrators: arXiv 1706.03762 Eq. (1) in PyTorch/TensorFlow.

Imports are lazy: NumPy-only users do not need either ML framework installed.
The operators assume matching batches and bool mask True=allowed; no dropout.
No model training, positional embeddings or multi-head projection is included.
"""
from __future__ import annotations

import math


def torch_indexed_sum(a, x):
    """y_i = Σ_j A_ij*x_j, preserving free index i."""
    import torch
    if a.ndim != 2 or x.ndim != 1 or a.shape[1] != x.shape[0]:
        raise ValueError('Expected A:(n,m), x:(m,)')
    if a.device != x.device or a.dtype != x.dtype:
        raise ValueError('Same dtype and device required')
    return torch.einsum('ij,j->i', a, x)


def tensorflow_indexed_sum(a, x):
    """y_i = Σ_j A_ij*x_j using TensorFlow axes (not reduce_sum of all axes)."""
    import tensorflow as tf
    a, x = tf.convert_to_tensor(a), tf.convert_to_tensor(x)
    if a.shape.rank != 2 or x.shape.rank != 1:
        raise ValueError('Expected A:(n,m), x:(m,)')
    if a.dtype != x.dtype:
        raise ValueError('Same dtype required')
    tf.debugging.assert_equal(tf.shape(a)[1], tf.shape(x)[0])
    return tf.einsum('ij,j->i', a, x)


def torch_attention(q, k, v, mask=None, *, return_weights=False):
    """Scaled dot-product attention, Eq.1; mask True means allowed."""
    import torch
    if not all(isinstance(a, torch.Tensor) for a in (q, k, v)):
        raise TypeError('Q, K and V must be torch.Tensor')
    if min(q.ndim, k.ndim, v.ndim) < 2:
        raise ValueError('Rank >= 2 required')
    if q.shape[:-2] != k.shape[:-2] or q.shape[:-2] != v.shape[:-2]:
        raise ValueError('Batch dimensions must agree (no implicit broadcasting)')
    if q.shape[-1] != k.shape[-1] or k.shape[-2] != v.shape[-2]:
        raise ValueError('Incompatible dk or key/value sequence')
    if any(s <= 0 for s in (q.shape[-2], k.shape[-2], q.shape[-1], v.shape[-1])):
        raise ValueError('Non-empty token/feature axes required')
    if q.dtype != k.dtype or q.dtype != v.dtype or not q.is_floating_point():
        raise TypeError('Equal floating dtypes required')
    if q.device != k.device or q.device != v.device:
        raise ValueError('All tensors must share device')
    if not all(torch.isfinite(a).all().item() for a in (q, k, v)):
        raise ValueError('Inputs must be finite')
    scores = (q @ k.transpose(-2, -1)) / math.sqrt(q.shape[-1])
    if not torch.isfinite(scores).all().item():
        raise ValueError('Nonfinite logits')
    if mask is not None:
        if not isinstance(mask, torch.Tensor) or mask.dtype != torch.bool:
            raise TypeError('Mask must be a boolean torch.Tensor (True=allowed)')
        if mask.device != q.device:
            raise ValueError('Mask must share device')
        try:
            allowed = torch.broadcast_to(mask, scores.shape)
        except RuntimeError as exc:
            raise ValueError('Mask shape cannot broadcast to scores') from exc
        if not torch.all(torch.any(allowed, dim=-1)).item():
            raise ValueError('Fully masked query row')
        scores = scores.masked_fill(~allowed, float('-inf'))
    weights = torch.softmax(scores, dim=-1)
    out = weights @ v
    return (out, weights) if return_weights else out


def tensorflow_attention(q, k, v, mask=None, *, return_weights=False):
    """TensorFlow-native Eq.1. Shape/finite assertions support eager and tf.function.

    Important: in graph mode, tf.debugging assertions may raise InvalidArgumentError.
    """
    import tensorflow as tf
    q, k, v = [tf.convert_to_tensor(t) for t in (q, k, v)]
    if any(a.shape.rank is None or a.shape.rank < 2 for a in (q, k, v)):
        raise ValueError('Known rank >=2 required')
    if q.shape.rank != k.shape.rank or q.shape.rank != v.shape.rank:
        raise ValueError('Ranks must match')
    if q.dtype != k.dtype or q.dtype != v.dtype or not q.dtype.is_floating:
        raise TypeError('Equal floating dtypes required')
    tf.debugging.assert_equal(tf.shape(q)[:-2], tf.shape(k)[:-2], message='Q/K batch mismatch')
    tf.debugging.assert_equal(tf.shape(q)[:-2], tf.shape(v)[:-2], message='Q/V batch mismatch')
    tf.debugging.assert_equal(tf.shape(q)[-1], tf.shape(k)[-1], message='dk mismatch')
    tf.debugging.assert_equal(tf.shape(k)[-2], tf.shape(v)[-2], message='Tk mismatch')
    tf.debugging.assert_positive(tf.shape(q)[-2:], message='Q axes must be > 0')
    tf.debugging.assert_positive(tf.shape(k)[-2:], message='K axes must be > 0')
    tf.debugging.assert_positive(tf.shape(v)[-2:], message='V axes must be > 0')
    for item in (q, k, v):
        tf.debugging.assert_all_finite(item, 'Inputs must be finite')
    # tf.math.rsqrt keeps runtime shape support (unlike Python math.sqrt on dynamic dims).
    scale = tf.math.rsqrt(tf.cast(tf.shape(q)[-1], dtype=q.dtype))
    scores = tf.linalg.matmul(q, k, transpose_b=True) * scale
    tf.debugging.assert_all_finite(scores, 'Nonfinite logits')
    if mask is not None:
        mask = tf.convert_to_tensor(mask)
        if mask.dtype != tf.bool:
            raise TypeError('Mask must be bool; True=allowed')
        allowed = tf.broadcast_to(mask, tf.shape(scores))
        tf.debugging.assert_equal(tf.reduce_all(tf.reduce_any(allowed, axis=-1)), True,
                                  message='Fully masked query row')
        scores = tf.where(allowed, scores, tf.cast(float('-inf'), scores.dtype))
    weights = tf.nn.softmax(scores, axis=-1)
    out = tf.linalg.matmul(weights, v)
    return (out, weights) if return_weights else out
