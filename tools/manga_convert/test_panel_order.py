#!/usr/bin/env python3
"""Unit tests for comic and manga panel reading order."""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert_manga import sort_panels_manga_order, sort_panels_reading_order


class PanelOrderTests(unittest.TestCase):
    def setUp(self):
        self.top_left = [0, 0, 40, 40]
        self.top_right = [60, 0, 100, 40]
        self.bottom_left = [0, 60, 40, 100]
        self.bottom_right = [60, 60, 100, 100]
        self.unsorted_grid = [self.bottom_left, self.top_right, self.bottom_right, self.top_left]

    def test_rtl_orders_each_tier_right_to_left(self):
        self.assertEqual(
            sort_panels_reading_order(self.unsorted_grid, "rtl"),
            [self.top_right, self.top_left, self.bottom_right, self.bottom_left],
        )

    def test_ltr_orders_each_tier_left_to_right(self):
        self.assertEqual(
            sort_panels_reading_order(self.unsorted_grid, "ltr"),
            [self.top_left, self.top_right, self.bottom_left, self.bottom_right],
        )

    def test_legacy_manga_helper_remains_rtl(self):
        self.assertEqual(
            sort_panels_manga_order(self.unsorted_grid),
            sort_panels_reading_order(self.unsorted_grid, "rtl"),
        )

    def test_invalid_direction_is_rejected(self):
        with self.assertRaises(ValueError):
            sort_panels_reading_order(self.unsorted_grid, "diagonal")


if __name__ == "__main__":
    unittest.main()
