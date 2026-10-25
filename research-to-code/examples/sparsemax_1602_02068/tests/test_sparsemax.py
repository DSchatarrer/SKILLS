"""Independent property-based / differential / gradient tests for arXiv:1602.02068v2.

Test sources: Eq. 2-4, Prop. 2, Eq. 6, Eq. 12, and Eq. 14.
Boundary gradients are not defined: gradient tests use strict interior points.
"""
import unittest
import importlib.util
import numpy as np
from sparsemax import (
    numpy_sparsemax as sparse,
    sparsemax_bisection_reference as bisect,
    sparsemax_jacobian_reference as jacobian,
    torch_sparsemax,
    tensorflow_sparsemax,
)


class TestSparsemaxNumpy(unittest.TestCase):
    def test_uniform_zero(self):
        np.testing.assert_allclose(sparse(np.zeros(5)), np.full(5, .2), atol=1e-14)

    def test_binary_hard_sigmoid_eq6(self):
        for t in [-3., -.8, 0., .6, 3.]:
            expected = np.clip((t + 1) / 2, 0, 1)
            self.assertAlmostEqual(sparse(np.array([t, 0.]))[0], expected, places=12)

    def test_simplex_invariants_and_exact_zeros(self):
        z = np.array([[3., -1., 0., 0.], [0.2, 0.1, -2, -.4]])
        p = sparse(z)
        np.testing.assert_allclose(p.sum(-1), np.ones(2), atol=1e-12)
        self.assertTrue(np.all(p >= 0))
        self.assertGreater(np.count_nonzero(p == 0), 0)

    def test_independent_bisection_random_sizes(self):
        rng = np.random.default_rng(160202068)
        for shape in [(1,), (2,), (5,), (3, 7), (2, 3, 11)]:
            z = rng.normal(size=shape)
            np.testing.assert_allclose(sparse(z), bisect(z), rtol=1e-12, atol=2e-12)

    def test_translation_invariance(self):
        rng = np.random.default_rng(6)
        z = rng.normal(size=(5, 13))
        np.testing.assert_allclose(sparse(z), sparse(z + 17.25), atol=5e-14)

    def test_permutation_invariance(self):
        z = np.array([3.1, -2., 1.3, 0.5, 0.1])
        perm = np.array([4, 0, 3, 2, 1])
        np.testing.assert_allclose(sparse(z[perm]), sparse(z)[perm], atol=1e-14)

    def test_jacobian_finite_difference(self):
        z = np.array([0.2, .15, -.9, 0.1], dtype=np.float64)
        analytical = jacobian(z)
        numerical = np.empty((4, 4))
        h = 1e-6
        for j in range(4):
            e = np.eye(4)[j] * h
            numerical[:, j] = (sparse(z+e) - sparse(z-e)) / (2*h)
        np.testing.assert_allclose(analytical, numerical, rtol=1e-8, atol=1e-9)

    @unittest.skipUnless(importlib.util.find_spec('scipy') is not None, 'SciPy no instalado')
    def test_constrained_optimization_eq2(self):
        """Independent constrained minimization: directly test the argmin definition."""
        from scipy.optimize import minimize
        for z in (np.array([.8, .2, -1., .4]), np.array([-2., -.3, 1., 1.2])):
            n = len(z)
            out = minimize(
                lambda p: .5*np.sum((p-z)**2),
                np.full(n, 1/n),
                jac=lambda p: p-z,
                bounds=[(0, None)]*n,
                constraints=[{'type': 'eq', 'fun': lambda p: np.sum(p)-1.,
                              'jac': lambda p: np.ones_like(p)}],
                method='SLSQP', options={'ftol': 1e-13, 'maxiter': 200},
            )
            self.assertTrue(out.success, out.message)
            np.testing.assert_allclose(sparse(z), out.x, atol=1e-7)

    def test_boundary_is_nondifferentiable(self):
        """At support-switch boundaries, central differences need not match autodiff."""
        z = np.array([.5, .1, -.2])  # tau=-.2 for the first two coordinates
        h = 1e-5
        delta = np.array([0., 0., h])
        up = (sparse(z+delta) - sparse(z))/h
        down = (sparse(z) - sparse(z-delta))/h
        self.assertGreater(np.max(np.abs(up-down)), .1)

    def test_bad_shapes_and_dtype(self):
        for z in (np.array(1.), np.array([]), np.array([1, 2]), np.array([np.nan, 2.])):
            with self.assertRaises(ValueError):
                sparse(z)

    def test_mutation_wrong_softmax_detected(self):
        z = np.array([3., 0., -2.])
        e = np.exp(z-np.max(z))
        wrong_softmax = e / e.sum()
        self.assertGreater(np.max(np.abs(wrong_softmax - sparse(z))), 1e-3)

    def test_mutation_wrong_axis_detected(self):
        z = np.array([[3.,0.,-2.],[.5,.3,-.8]])
        wrong_sum = sparse(z.T).T
        self.assertGreater(np.max(np.abs(wrong_sum.sum(-1)-1.)), .01)


class TestSparsemaxTorch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import torch
            cls.torch = torch
        except ImportError:
            raise unittest.SkipTest('PyTorch no instalado')

    def test_matches_numpy(self):
        z = np.random.default_rng(1234).normal(size=(5, 8))
        out = torch_sparsemax(self.torch.tensor(z, dtype=self.torch.float64)).detach().numpy()
        np.testing.assert_allclose(out, sparse(z), atol=1e-12)

    def test_backward_matches_equation12(self):
        z = self.torch.tensor([.2,.15,-.9,.1], dtype=self.torch.float64, requires_grad=True)
        got = self.torch.autograd.functional.jacobian(torch_sparsemax, z).detach().numpy()
        np.testing.assert_allclose(got, jacobian(z.detach().numpy()), atol=1e-12)

    def test_gradcheck(self):
        from torch.autograd import gradcheck
        z = self.torch.tensor([[.2,.15,-.9,.1],[.5,.1,-3., -0.4]], dtype=self.torch.float64, requires_grad=True)
        self.assertTrue(gradcheck(torch_sparsemax, (z,), eps=1e-6, atol=1e-5, rtol=1e-4))

    def test_incorrect_dtype(self):
        with self.assertRaises(ValueError):
            torch_sparsemax(self.torch.tensor([1,2]))


@unittest.skipUnless(importlib.util.find_spec("tensorflow") is not None, "TensorFlow no instalado; pendiente")
class TestSparsemaxTensorflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import tensorflow as tf
            cls.tf = tf
        except ImportError:
            raise unittest.SkipTest('TensorFlow no instalado; no se declara probado')

    def test_matches_numpy_and_graph_mode(self):
        tf = self.tf
        z = np.random.default_rng(12).normal(size=(3, 8))
        input_ = tf.constant(z, dtype=tf.float64)
        want = sparse(z)
        np.testing.assert_allclose(tensorflow_sparsemax(input_).numpy(), want, atol=1e-12)
        np.testing.assert_allclose(tf.function(tensorflow_sparsemax)(input_).numpy(), want, atol=1e-12)

    def test_gradient_matches_jacobian(self):
        tf = self.tf
        x = tf.Variable([.2,.15,-.9,.1], dtype=tf.float64)
        with tf.GradientTape() as tape:
            y = tensorflow_sparsemax(x)
        j = tape.jacobian(y, x)
        np.testing.assert_allclose(j.numpy(), jacobian(x.numpy()), atol=1e-12)

    def test_dynamic_batch_dimension_graph(self):
        tf = self.tf
        @tf.function(input_signature=[tf.TensorSpec([None, 4], dtype=tf.float64)])
        def project(x):
            return tensorflow_sparsemax(x)
        for size in (1, 3):
            z = np.random.default_rng(size).normal(size=(size, 4))
            np.testing.assert_allclose(project(tf.constant(z)).numpy(), sparse(z), atol=1e-12)


if __name__ == '__main__':
    unittest.main()
