#!/usr/bin/env python3
"""Unit tests for comic and manga panel reading order."""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert_manga import (
    detect_panels,
    resolve_reading_direction,
    sort_panels_manga_order,
    sort_panels_reading_order,
)


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


class ConversionProfileTests(unittest.TestCase):
    def test_manga_defaults_to_rtl(self):
        self.assertEqual(resolve_reading_direction("manga", None), "rtl")

    def test_western_defaults_to_ltr(self):
        self.assertEqual(resolve_reading_direction("western", None), "ltr")

    def test_explicit_direction_overrides_profile_default(self):
        self.assertEqual(resolve_reading_direction("western", "rtl"), "rtl")

    @patch("convert_manga._detect_panels_grid", return_value=[[1, 2, 3, 4]])
    @patch("convert_manga._detect_panels_yolo")
    def test_western_profile_bypasses_manga_model(self, manga_detector, gutter_detector):
        self.assertEqual(detect_panels(object(), "western"), [[1, 2, 3, 4]])
        manga_detector.assert_not_called()
        gutter_detector.assert_called_once()

    @patch("convert_manga._detect_panels_grid", return_value=[[5, 6, 7, 8]])
    @patch("convert_manga._detect_panels_yolo", return_value=None)
    def test_manga_profile_falls_back_to_gutters(self, manga_detector, gutter_detector):
        self.assertEqual(detect_panels(object(), "manga"), [[5, 6, 7, 8]])
        manga_detector.assert_called_once()
        gutter_detector.assert_called_once()


if __name__ == "__main__":
    unittest.main()
