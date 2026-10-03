import unittest

from anomaly_detection import find_amount_outliers


class AnomalyDetectionTests(unittest.TestCase):
    def test_flags_a_large_outlier(self):
        self.assertEqual(find_amount_outliers([10, 11, 9, 10, 100], z_threshold=1.5), [100.0])

    def test_ignores_constant_values(self):
        self.assertEqual(find_amount_outliers([10, 10, 10]), [])
