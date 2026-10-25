"""Framework-specific mathematical, regression and gradient tests.

Unavailable frameworks are SKIPPED, not treated as passed.
"""
from __future__ import annotations

import importlib.util
import math
import unittest

import numpy as np

from framework_ops import (tensorflow_attention, tensorflow_indexed_sum,
                           torch_attention, torch_indexed_sum)

HAS_TORCH = importlib.util.find_spec('torch') is not None
HAS_TF = importlib.util.find_spec('tensorflow') is not None


def inputs():
    rng = np.random.default_rng(123)
    return (rng.normal(size=(2, 3, 4)).astype('float64'),
            rng.normal(size=(2, 5, 4)).astype('float64'),
            rng.normal(size=(2, 5, 2)).astype('float64'))


def oracle(q, k, v, mask=None):
    """Independent NumPy scalar loops; can include batches."""
    out = np.empty(q.shape[:-2] + (q.shape[-2], v.shape[-1]), dtype=float)
    for batch in np.ndindex(q.shape[:-2]):
        for i in range(q.shape[-2]):
            eligible = [j for j in range(k.shape[-2]) if mask is None or mask[i, j]]
            s = [sum(float(q[batch + (i, d)]) * float(k[batch + (j, d)])
                     for d in range(q.shape[-1])) / math.sqrt(q.shape[-1]) for j in eligible]
            exps = [math.exp(x - max(s)) for x in s]
            for f in range(v.shape[-1]):
                out[batch + (i, f)] = sum(e / sum(exps) * float(v[batch + (j, f)])
                                               for e, j in zip(exps, eligible))
    return out


@unittest.skipUnless(HAS_TORCH, 'PyTorch not installed: tests NOT executed')
class TorchTests(unittest.TestCase):
    def setUp(self):
        import torch
        self.torch = torch
        self.q, self.k, self.v = [torch.tensor(a, dtype=torch.float64) for a in inputs()]

    def test_indexed_sum_and_shapes(self):
        a = self.torch.tensor([[1.,2.],[3.,4.]], dtype=self.torch.float64)
        x = self.torch.tensor([5.,6.], dtype=self.torch.float64)
        np.testing.assert_allclose(torch_indexed_sum(a,x).numpy(), [17.,39.])

    def test_attention_vs_independent_scalar_oracle(self):
        expected = oracle(*inputs())
        np.testing.assert_allclose(torch_attention(self.q,self.k,self.v).numpy(), expected, rtol=1e-12, atol=1e-12)

    def test_masks_weights_and_batches(self):
        mask = self.torch.tensor([[True, False, True, True, True]]*3)
        out, weights = torch_attention(self.q,self.k,self.v,mask,return_weights=True)
        self.assertEqual(tuple(out.shape), (2,3,2))
        self.assertEqual(tuple(weights.shape), (2,3,5))
        np.testing.assert_allclose(weights.sum(-1).numpy(), 1., atol=1e-12)
        np.testing.assert_array_equal(weights[..., 1].numpy(), 0.)
        np.testing.assert_allclose(out.numpy(), oracle(*inputs(), mask.numpy()), rtol=1e-12, atol=1e-12)

    def test_wrong_scale_mutation_is_detected(self):
        q=self.torch.tensor([[2.,0.]],dtype=self.torch.float64)
        k=self.torch.tensor([[1.,0.],[0.,1.]],dtype=self.torch.float64)
        v=self.torch.tensor([[1.],[0.]],dtype=self.torch.float64)
        correct=torch_attention(q,k,v)[0,0].item()
        wrong=self.torch.softmax((q@k.T)/q.shape[-1],dim=-1)@v
        self.assertGreater(abs(correct-wrong[0,0].item()),0.04)

    def test_bad_masks_rejected(self):
        with self.assertRaises(ValueError):
            torch_attention(self.q,self.k,self.v,self.torch.zeros(3,5,dtype=self.torch.bool))
        with self.assertRaises(TypeError):
            torch_attention(self.q,self.k,self.v,self.torch.ones(3,5))

    def test_autograd_gradcheck(self):
        import torch
        q=self.q.clone().requires_grad_()
        k=self.k.clone().requires_grad_()
        v=self.v.clone().requires_grad_()
        self.assertTrue(torch.autograd.gradcheck(lambda q,k,v: torch_attention(q,k,v), (q,k,v), eps=1e-6,atol=1e-5,rtol=1e-3))

    def test_autograd_reaches_each_input(self):
        q=self.q.clone().requires_grad_()
        k=self.k.clone().requires_grad_()
        v=self.v.clone().requires_grad_()
        (torch_attention(q,k,v)**2).sum().backward()
        for x in (q,k,v):
            self.assertIsNotNone(x.grad)
            self.assertTrue(self.torch.isfinite(x.grad).all().item())
            self.assertGreater(x.grad.abs().sum().item(),0)

    def test_pytorch_builtin_equivalence(self):
        from torch.nn.functional import scaled_dot_product_attention as sdpa
        mask=self.torch.tensor([[True,False,True,True,True]]*3)
        expected=sdpa(self.q,self.k,self.v,attn_mask=mask,dropout_p=0.0)
        np.testing.assert_allclose(torch_attention(self.q,self.k,self.v,mask).numpy(),expected.numpy(),rtol=1e-12,atol=1e-12)

    def test_extreme_scores_stable(self):
        q=self.torch.tensor([[1000.,0.]],dtype=self.torch.float64)
        k=self.torch.tensor([[1000.,0.],[-1000.,0.]],dtype=self.torch.float64)
        v=self.torch.tensor([[7.],[-2.]],dtype=self.torch.float64)
        np.testing.assert_allclose(torch_attention(q,k,v).numpy(), [[7.]])


@unittest.skipUnless(HAS_TF, 'TensorFlow not installed: tests NOT executed')
class TensorFlowTests(unittest.TestCase):
    def setUp(self):
        import tensorflow as tf
        self.tf = tf
        self.q,self.k,self.v = [tf.constant(x,dtype=tf.float64) for x in inputs()]

    def test_indexed_sum_and_shapes(self):
        tf=self.tf
        a=tf.constant([[1.,2.],[3.,4.]],dtype=tf.float64)
        x=tf.constant([5.,6.],dtype=tf.float64)
        np.testing.assert_allclose(tensorflow_indexed_sum(a,x).numpy(),[17.,39.])

    def test_attention_vs_independent_scalar_oracle(self):
        np.testing.assert_allclose(tensorflow_attention(self.q,self.k,self.v).numpy(),oracle(*inputs()),rtol=1e-12,atol=1e-12)

    def test_masks_weights_and_batches(self):
        mask=self.tf.constant([[True,False,True,True,True]]*3)
        out, weights=tensorflow_attention(self.q,self.k,self.v,mask,return_weights=True)
        self.assertEqual(tuple(out.shape),(2,3,2))
        self.assertEqual(tuple(weights.shape),(2,3,5))
        np.testing.assert_allclose(self.tf.reduce_sum(weights,axis=-1).numpy(),1,atol=1e-12)
        np.testing.assert_array_equal(weights[...,1].numpy(),0.)
        np.testing.assert_allclose(out.numpy(),oracle(*inputs(),mask.numpy()),rtol=1e-12,atol=1e-12)

    def test_wrong_scale_mutation_is_detected(self):
        tf=self.tf
        q=tf.constant([[2.,0.]],dtype=tf.float64)
        k=tf.constant([[1.,0.],[0.,1.]],dtype=tf.float64)
        v=tf.constant([[1.],[0.]],dtype=tf.float64)
        correct=tensorflow_attention(q,k,v).numpy()[0,0]
        wrong=tf.linalg.matmul(tf.nn.softmax(tf.linalg.matmul(q,k,transpose_b=True)/2.,axis=-1),v).numpy()[0,0]
        self.assertGreater(abs(correct-wrong),0.04)

    def test_bad_masks_rejected(self):
        tf=self.tf
        with self.assertRaises(tf.errors.InvalidArgumentError):
            tensorflow_attention(self.q,self.k,self.v,tf.zeros((3,5),dtype=tf.bool))
        with self.assertRaises(TypeError):
            tensorflow_attention(self.q,self.k,self.v,tf.ones((3,5)))

    def test_gradient_tape_finite_differences(self):
        tf=self.tf
        q=tf.Variable(self.q)
        with tf.GradientTape() as tape:
            loss=tf.reduce_sum(tensorflow_attention(q,self.k,self.v)**2)
        analytic=tape.gradient(loss,q).numpy()
        self.assertIsNotNone(analytic)
        delta=1e-5
        base=q.numpy()
        plus=base.copy(); plus[0,0,0]+=delta
        minus=base.copy(); minus[0,0,0]-=delta
        fp=tf.reduce_sum(tensorflow_attention(plus,self.k,self.v)**2).numpy()
        fm=tf.reduce_sum(tensorflow_attention(minus,self.k,self.v)**2).numpy()
        self.assertAlmostEqual(analytic[0,0,0],(fp-fm)/(2*delta),places=6)

    def test_gradient_tape_all_inputs(self):
        tf=self.tf
        q,k,v=[tf.Variable(x) for x in (self.q,self.k,self.v)]
        with tf.GradientTape() as tape:
            loss=tf.reduce_sum(tensorflow_attention(q,k,v)**2)
        grads=tape.gradient(loss,[q,k,v])
        for grad in grads:
            self.assertIsNotNone(grad)
            self.assertTrue(bool(tf.reduce_all(tf.math.is_finite(grad)).numpy()))
            self.assertGreater(float(tf.reduce_sum(tf.abs(grad)).numpy()),0)

    def test_tf_function_graph_mode(self):
        tf=self.tf
        @tf.function
        def graph_fn(q,k,v):
            return tensorflow_attention(q,k,v)
        np.testing.assert_allclose(graph_fn(self.q,self.k,self.v).numpy(), oracle(*inputs()),rtol=1e-12,atol=1e-12)

    def test_extreme_scores_stable(self):
        tf=self.tf
        q=tf.constant([[1000.,0.]],dtype=tf.float64)
        k=tf.constant([[1000.,0.],[-1000.,0.]],dtype=tf.float64)
        v=tf.constant([[7.],[-2.]],dtype=tf.float64)
        np.testing.assert_allclose(tensorflow_attention(q,k,v).numpy(),[[7.]])


@unittest.skipUnless(HAS_TORCH and HAS_TF, 'Cross-framework tests require BOTH PyTorch and TensorFlow')
class CrossBackendTests(unittest.TestCase):
    def test_attention_outputs_agree(self):
        import torch
        import tensorflow as tf
        q,k,v=inputs()
        q_t,k_t,v_t=[torch.tensor(x,dtype=torch.float64) for x in (q,k,v)]
        q_f,k_f,v_f=[tf.constant(x,dtype=tf.float64) for x in (q,k,v)]
        np.testing.assert_allclose(torch_attention(q_t,k_t,v_t).detach().numpy(),
                                   tensorflow_attention(q_f,k_f,v_f).numpy(),atol=1e-12,rtol=1e-12)

    def test_attention_gradients_agree(self):
        import torch
        import tensorflow as tf
        q,k,v=inputs()
        q_t=torch.tensor(q,dtype=torch.float64,requires_grad=True)
        k_t=torch.tensor(k,dtype=torch.float64)
        v_t=torch.tensor(v,dtype=torch.float64)
        gt=torch.autograd.grad((torch_attention(q_t,k_t,v_t)**2).sum(),q_t)[0].numpy()
        q_f=tf.Variable(q,dtype=tf.float64)
        with tf.GradientTape() as tape:
            gf_loss=tf.reduce_sum(tensorflow_attention(q_f,k,v)**2)
        gf=tape.gradient(gf_loss,q_f).numpy()
        np.testing.assert_allclose(gt,gf,atol=1e-10,rtol=1e-9)


if __name__=='__main__':
    unittest.main()
