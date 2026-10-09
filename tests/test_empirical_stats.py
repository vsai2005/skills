import unittest

from scripts.empirical_stats import bootstrap_mean_ci, exact_sign_test_pvalue, win_rate


class EmpiricalStatsTests(unittest.TestCase):
    def test_positive_repeated_deltas_have_positive_interval(self):
        values = [0.2, 0.1, 0.15, 0.2, 0.1]
        low, high = bootstrap_mean_ci(values, samples=1000, seed=7)
        self.assertGreater(low, 0)
        self.assertGreater(high, low)
        self.assertEqual(1.0, win_rate(values))

    def test_sign_test_ignores_ties_and_is_exact(self):
        # Five wins, no losses -> two-sided exact sign p = 2/32 = 0.0625.
        self.assertAlmostEqual(0.0625, exact_sign_test_pvalue([1, 1, 1, 1, 1, 0]), places=6)

    def test_bootstrap_rejects_too_few_samples(self):
        with self.assertRaises(ValueError):
            bootstrap_mean_ci([0.1, 0.2], samples=10)


if __name__ == "__main__":
    unittest.main()
