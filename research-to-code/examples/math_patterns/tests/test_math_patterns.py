import unittest
import numpy as np
from math_patterns import indexed_sum_loops, indexed_sum_vectorized, linear_recurrence, weighted_expectation


class MathNotationTranslationTests(unittest.TestCase):
    def test_indexed_sum_manual_case(self):
        a = np.array([[1., 2.], [3., 4.], [5., 6.]])
        x = np.array([7., 8.])
        result = indexed_sum_vectorized(a, x)
        np.testing.assert_array_equal(result, [23., 53., 83.])
        self.assertEqual(result.shape, (3,))
        np.testing.assert_array_equal(indexed_sum_loops(a, x), result)

    def test_non_square_matrix_detects_axis_conflation(self):
        a = np.arange(15.).reshape(3, 5)
        x = np.arange(5.)
        self.assertEqual(indexed_sum_vectorized(a, x).shape, (3,))
        self.assertEqual(indexed_sum_loops(a, x).shape, (3,))

    def test_indexed_sum_rejects_bad_shape(self):
        with self.assertRaises(ValueError):
            indexed_sum_vectorized(np.ones((2, 3)), np.ones(2))

    def test_weighted_expectation_vs_mean(self):
        self.assertAlmostEqual(weighted_expectation([2, 10], [.9, .1]), 2.8)
        self.assertNotAlmostEqual(weighted_expectation([2, 10], [.9, .1]), 6.)

    def test_invalid_distribution_is_rejected(self):
        for bad in ([-.1, 1.1], [.1, .1], [np.nan, 1]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                weighted_expectation([2, 10], bad)

    def test_uniform_distribution_equals_arithmetic_mean(self):
        self.assertAlmostEqual(weighted_expectation([2, 10], [.5, .5]), 6.)

    def test_recurrence_has_t_plus_one_states(self):
        a = np.array([[2.]])
        b = np.array([[1.]])
        x = np.array([[3.], [4.], [-2.]])
        out = linear_recurrence(a, b, x, np.array([1.]))
        np.testing.assert_array_equal(out[:, 0], [1., 5., 14., 26.])
        self.assertEqual(out.shape, (4, 1))

    def test_empty_sequence_includes_initial_state(self):
        out = linear_recurrence(np.eye(2), np.eye(2), np.empty((0, 2)), np.array([1., 2.]))
        np.testing.assert_array_equal(out, [[1., 2.]])


if __name__ == "__main__":
    unittest.main()
