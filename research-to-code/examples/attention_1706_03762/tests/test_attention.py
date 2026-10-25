"""Math, adversarial, metamorphic and regression checks of Eq. 1 only."""
import unittest

import numpy as np

from attention import attention_reference_loops, scaled_dot_product_attention


class AttentionTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(314159)
        self.q = rng.normal(size=(3, 4))
        self.k = rng.normal(size=(5, 4))
        self.v = rng.normal(size=(5, 2))

    def test_reference_vs_vectorized(self):
        actual = scaled_dot_product_attention(self.q, self.k, self.v)
        expected = attention_reference_loops(self.q, self.k, self.v)
        np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)

    def test_scaling_sqrt_dk_not_dk_or_no_scaling(self):
        q = np.array([[2., 0.]])
        k = np.array([[1., 0.], [0., 1.]])
        v = np.array([[1.], [0.]])
        expected = np.exp(np.sqrt(2.)) / (1 + np.exp(np.sqrt(2.)))
        self.assertAlmostEqual(scaled_dot_product_attention(q, k, v)[0, 0], expected, places=12)

    def test_output_dimensions_and_weights(self):
        out, weights = scaled_dot_product_attention(self.q, self.k, self.v, return_weights=True)
        self.assertEqual(out.shape, (3, 2))
        self.assertEqual(weights.shape, (3, 5))
        np.testing.assert_allclose(weights.sum(axis=-1), 1, atol=1e-12)
        self.assertTrue(np.all(weights >= 0))

    def test_uniform_keys_produce_mean_values(self):
        keys = np.ones_like(self.k)
        expected = np.broadcast_to(self.v.mean(axis=0), (3, 2))
        np.testing.assert_allclose(scaled_dot_product_attention(self.q, keys, self.v), expected)

    def test_joint_key_value_permutation(self):
        order = [4, 0, 2, 1, 3]
        before = scaled_dot_product_attention(self.q, self.k, self.v)
        after = scaled_dot_product_attention(self.q, self.k[order], self.v[order])
        np.testing.assert_allclose(before, after, rtol=1e-12, atol=1e-12)

    def test_mask_disables_key_exactly(self):
        mask = np.array([True, False, True, False, True])
        out, weights = scaled_dot_product_attention(self.q, self.k, self.v, mask, return_weights=True)
        np.testing.assert_array_equal(weights[:, ~mask], 0)
        np.testing.assert_allclose(out, attention_reference_loops(self.q, self.k, self.v, mask))

    def test_causal_mask_future_invariance(self):
        q = self.q
        k = self.k[:3].copy()
        v = self.v[:3].copy()
        causal = np.tril(np.ones((3, 3), dtype=bool))
        original = scaled_dot_product_attention(q, k, v, causal)
        k[-1, :] += 200.0
        v[-1, :] += 300.0
        changed = scaled_dot_product_attention(q, k, v, causal)
        np.testing.assert_allclose(original[:2], changed[:2], rtol=0, atol=1e-12)

    def test_batched_case_and_reference(self):
        qb = np.stack([self.q, 2 * self.q])
        kb = np.stack([self.k, self.k])
        vb = np.stack([self.v, -self.v])
        out = scaled_dot_product_attention(qb, kb, vb)
        self.assertEqual(out.shape, (2, 3, 2))
        np.testing.assert_allclose(out, attention_reference_loops(qb, kb, vb), rtol=1e-12, atol=1e-12)

    def test_high_scores_stable(self):
        q = np.array([[1000., 0.]])
        k = np.array([[1000., 0.], [-1000., 0.]])
        v = np.array([[7.], [-2.]])
        out = scaled_dot_product_attention(q, k, v)
        self.assertTrue(np.all(np.isfinite(out)))
        np.testing.assert_allclose(out, [[7.]], atol=1e-12)

    def test_all_masked_row_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "ninguna clave"):
            scaled_dot_product_attention(self.q, self.k, self.v, mask=np.zeros((3, 5), dtype=bool))

    def test_bad_dims_rejected(self):
        with self.assertRaises(ValueError):
            scaled_dot_product_attention(self.q, self.k[:, :2], self.v)
        with self.assertRaises(ValueError):
            scaled_dot_product_attention(self.q, self.k, self.v[:-1])

    def test_wrong_mask_type_and_shape_rejected(self):
        with self.assertRaises(TypeError):
            scaled_dot_product_attention(self.q, self.k, self.v, np.ones((3, 5)))
        with self.assertRaises(ValueError):
            scaled_dot_product_attention(self.q, self.k, self.v, np.ones((4, 5), dtype=bool))

    def test_nonfinite_inputs_rejected(self):
        bad = self.q.copy()
        bad[0, 0] = np.nan
        with self.assertRaises(ValueError):
            scaled_dot_product_attention(bad, self.k, self.v)

    def test_empty_features_rejected(self):
        with self.assertRaises(ValueError):
            scaled_dot_product_attention(self.q[:, :0], self.k[:, :0], self.v)


if __name__ == "__main__":
    unittest.main()
