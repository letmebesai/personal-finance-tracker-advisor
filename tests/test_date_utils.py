import unittest
from datetime import date

from date_utils import month_bounds, parse_iso_date


class DateUtilityTests(unittest.TestCase):
    def test_parses_iso_dates(self):
        self.assertEqual(parse_iso_date("2026-02-03"), date(2026, 2, 3))

    def test_calculates_leap_year_month_bounds(self):
        self.assertEqual(month_bounds("2024-02-15"), (date(2024, 2, 1), date(2024, 2, 29)))
