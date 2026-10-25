import unittest
import numpy as np
from expectation import weighted_expectation, weighted_expectation_reference


class LocalSpecTests(unittest.TestCase):
    def test_hand_calculated_case(self):
        self.assertAlmostEqual(weighted_expectation([2,10],[.9,.1]),2.8)
        self.assertNotAlmostEqual(weighted_expectation([2,10],[.9,.1]),6)

    def test_random_reference_equivalence(self):
        rng=np.random.default_rng(2026)
        for n in (1,2,5,17):
            x=rng.normal(size=n)
            p=rng.random(size=n); p/=p.sum()
            np.testing.assert_allclose(weighted_expectation(x,p),weighted_expectation_reference(x,p),rtol=1e-12,atol=1e-12)

    def test_translation_invariance(self):
        x=[1,3,9]; p=[.1,.2,.7]
        self.assertAlmostEqual(weighted_expectation(np.array(x)+5,p),weighted_expectation(x,p)+5)

    def test_rejects_bad_weights(self):
        for weights in ([.3,.3],[-.1,1.1],[0,0]):
            with self.subTest(weights=weights):
                with self.assertRaises(ValueError): weighted_expectation([2,10],weights)

    def test_rejects_shape_mismatch_not_broadcast(self):
        with self.assertRaises(ValueError): weighted_expectation([[1,2]],[[.2,.8]])
        with self.assertRaises(ValueError): weighted_expectation([1,2],[1])

    def test_rejects_nonfinite(self):
        with self.assertRaises(ValueError): weighted_expectation([1,float('nan')],[.5,.5])
        with self.assertRaises(ValueError): weighted_expectation([1,2],[float('inf'),0])
