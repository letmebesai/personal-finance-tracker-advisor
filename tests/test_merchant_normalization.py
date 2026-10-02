import unittest

from merchant_normalization import normalize_merchant


class MerchantNormalizationTests(unittest.TestCase):
    def test_removes_payment_noise(self):
        self.assertEqual(normalize_merchant("UPI-PAYMENT-Swiggy!"), "SWIGGY")

    def test_preserves_meaningful_words_and_digits(self):
        self.assertEqual(normalize_merchant("POS Netflix 2026"), "NETFLIX 2026")


if __name__ == "__main__":
    unittest.main()
