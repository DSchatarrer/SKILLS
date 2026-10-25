"""arXiv:1706.03762v7, Sec. 3.2.1, Eq. (1): scaled dot-product attention.

LIMITATION: This is one mathematical operator, NOT a complete Transformer.
Shapes: Q(..., Tq, dk), K(..., Tk, dk), V(..., Tk, dv).
Leading batch axes must match, no implicit batch broadcasting. The optional mask
has True at *allowed* (query,key) positions and must broadcast to (...,Tq,Tk).
Fully masked query rows are explicitly rejected (not defined by the paper Eq.1).
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np


def _validate(q: np.ndarray, k: np.ndarray, v: np.ndarray) -> None:
    if min(q.ndim, k.ndim, v.ndim) < 2:
        raise ValueError("Q, K y V requieren shape (..., tokens, features)")
    if q.ndim != k.ndim or q.ndim != v.ndim or q.shape[:-2] != k.shape[:-2] or q.shape[:-2] != v.shape[:-2]:
        raise ValueError("Q, K y V deben compartir shape de lote")
    if q.shape[-1] != k.shape[-1] or k.shape[-2] != v.shape[-2]:
        raise ValueError("Incompatibilidad entre dimensiones dk/Tk")
    if min(q.shape[-2], k.shape[-2], v.shape[-1], q.shape[-1]) == 0:
        raise ValueError("Dimensiones de secuencia/features deben ser positivas")
    if any(a.dtype.kind != "f" for a in (q, k, v)):
        raise TypeError("Solo arrays de coma flotante")
    if not all(np.all(np.isfinite(a)) for a in (q, k, v)):
        raise ValueError("Q, K y V deben ser finitos")


def _mask_for_shape(mask: Optional[np.ndarray], shape: tuple[int, ...]) -> np.ndarray:
    if mask is None:
        return np.ones(shape, dtype=bool)
    raw = np.asarray(mask)
    if raw.dtype != bool:
        raise TypeError("La máscara debe ser booleana: True indica token permitido")
    try:
        allowed = np.broadcast_to(raw, shape)
    except ValueError as exc:
        raise ValueError(f"Mask shape {raw.shape} no compatible con {shape}") from exc
    if not np.all(np.any(allowed, axis=-1)):
        raise ValueError("Hay una consulta sin ninguna clave permitida")
    return allowed


def scaled_dot_product_attention(
    q: np.ndarray, k: np.ndarray, v: np.ndarray,
    mask: Optional[np.ndarray] = None, *, return_weights: bool = False,
) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
    """Softmax(Q @ K.T / sqrt(dk)) @ V with stable, last-axis softmax."""
    q, k, v = np.asarray(q), np.asarray(k), np.asarray(v)
    _validate(q, k, v)
    scores = np.matmul(q, np.swapaxes(k, -1, -2)) / math.sqrt(q.shape[-1])
    if not np.all(np.isfinite(scores)):
        raise ValueError("Score no finito; reduzca rango/ajuste precisión numérica")
    allowed = _mask_for_shape(mask, scores.shape)
    masked_scores = np.where(allowed, scores, -np.inf)
    shifted = masked_scores - np.max(masked_scores, axis=-1, keepdims=True)
    weights = np.where(allowed, np.exp(shifted), 0.0)
    weights /= weights.sum(axis=-1, keepdims=True)
    out = weights @ v
    return (out, weights) if return_weights else out


def attention_reference_loops(
    q: np.ndarray, k: np.ndarray, v: np.ndarray, mask: Optional[np.ndarray] = None
) -> np.ndarray:
    """Independent, deliberately slow loop formulation of the same equation.

    Works on a single (Q,K,V) slice or on matching batches. Uses math.exp for
    a scalar oracle; does not reuse the vectorized softmax or matrix product.
    """
    q, k, v = np.asarray(q), np.asarray(k), np.asarray(v)
    _validate(q, k, v)
    mask_np = _mask_for_shape(mask, q.shape[:-2] + (q.shape[-2], k.shape[-2]))
    result = np.empty(q.shape[:-2] + (q.shape[-2], v.shape[-1]), dtype=np.float64)
    for batch_index in np.ndindex(q.shape[:-2]):
        for i in range(q.shape[-2]):
            valid_j = [j for j in range(k.shape[-2]) if mask_np[batch_index + (i, j)]]
            raw = []
            for j in valid_j:
                dot = sum(float(q[batch_index + (i, d)]) * float(k[batch_index + (j, d)])
                          for d in range(q.shape[-1]))
                raw.append(dot / math.sqrt(q.shape[-1]))
            max_raw = max(raw)
            exponentials = [math.exp(value - max_raw) for value in raw]
            z = sum(exponentials)
            for feature in range(v.shape[-1]):
                result[batch_index + (i, feature)] = sum(
                    (exponentials[index] / z) * float(v[batch_index + (j, feature)])
                    for index, j in enumerate(valid_j)
                )
    return result
