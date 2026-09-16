#!/usr/bin/env python3
"""Image-level tests for irregular western-comic panel detection."""

import sys
import unittest
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:  # The converter documents Pillow as a runtime dependency.
    Image = None

sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert_manga import (
    detect_panels,
    scale_panel_boxes,
    sort_panels_reading_order,
    split_spread_image,
)


@unittest.skipIf(Image is None, "Pillow is required for image-level detector tests")
class WesternPanelDetectionTests(unittest.TestCase):
    @staticmethod
    def page_with_panels(boxes, size=(600, 900)):
        image = Image.new("RGB", size, "white")
        draw = ImageDraw.Draw(image)
        for box in boxes:
            draw.rectangle(box, fill="gray", outline="black", width=5)
        return image

    def test_regular_two_by_two_grid(self):
        image = self.page_with_panels(
            [(20, 20, 285, 425), (315, 20, 580, 425),
             (20, 455, 285, 880), (315, 455, 580, 880)]
        )
        panels = sort_panels_reading_order(detect_panels(image, "western"), "ltr")
        self.assertEqual(len(panels), 4)
        self.assertLess(panels[0][0], panels[1][0])
        self.assertLess(panels[0][1], panels[2][1])

    def test_tall_panel_beside_two_stacked_panels(self):
        image = self.page_with_panels(
            [(20, 20, 280, 880), (320, 20, 580, 425), (320, 455, 580, 880)]
        )
        panels = detect_panels(image, "western")
        self.assertEqual(len(panels), 3)
        widths = [panel[2] - panel[0] for panel in panels]
        heights = [panel[3] - panel[1] for panel in panels]
        self.assertGreater(max(heights), 2 * min(heights))
        self.assertLess(max(widths) - min(widths), 40)

    def test_two_side_by_side_panels_with_independent_internal_rows(self):
        image = self.page_with_panels(
            [(20, 20, 280, 280), (20, 320, 280, 880),
             (320, 20, 580, 580), (320, 620, 580, 880)]
        )
        panels = detect_panels(image, "western")
        self.assertEqual(len(panels), 4)

    def test_dark_gutters_split_light_panels(self):
        image = Image.new("RGB", (600, 900), "black")
        draw = ImageDraw.Draw(image)
        for box in [(20, 20, 285, 425), (315, 20, 580, 425),
                    (20, 455, 285, 880), (315, 455, 580, 880)]:
            draw.rectangle(box, fill="gray", outline="white", width=5)
        self.assertEqual(len(detect_panels(image, "western")), 4)

    def test_solid_dark_page_degrades_to_full_page(self):
        image = Image.new("RGB", (600, 900), "black")
        self.assertEqual(detect_panels(image, "western"), [[0, 0, 600, 900]])

    def test_borderless_page_degrades_to_full_page(self):
        image = Image.new("RGB", (600, 900), "gray")
        self.assertEqual(detect_panels(image, "western"), [[0, 0, 600, 900]])

    def test_source_resolution_boxes_scale_to_x3_page_space(self):
        boxes = [[0, 0, 600, 900], [315, 455, 580, 880]]
        self.assertEqual(
            scale_panel_boxes(boxes, (600, 900), (352, 528)),
            [[0, 0, 352, 528], [185, 267, 340, 516]],
        )

    def test_scaled_tiny_box_remains_nonempty(self):
        self.assertEqual(
            scale_panel_boxes([[599, 899, 600, 900]], (600, 900), (352, 528)),
            [[351, 527, 352, 528]],
        )

    def test_ltr_spread_splits_left_then_right(self):
        image = Image.new("RGB", (8, 4), "white")
        ImageDraw.Draw(image).rectangle((0, 0, 3, 3), fill="black")
        parts = split_spread_image(image, "ltr")
        self.assertEqual([part.size for part in parts], [(4, 4), (4, 4)])
        self.assertEqual(parts[0].getpixel((0, 0)), (0, 0, 0))
        self.assertEqual(parts[1].getpixel((0, 0)), (255, 255, 255))

    def test_rtl_spread_splits_right_then_left(self):
        image = Image.new("RGB", (8, 4), "white")
        ImageDraw.Draw(image).rectangle((0, 0, 3, 3), fill="black")
        parts = split_spread_image(image, "rtl")
        self.assertEqual(parts[0].getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(parts[1].getpixel((0, 0)), (0, 0, 0))

    def test_portrait_page_is_not_split(self):
        image = Image.new("RGB", (4, 8), "white")
        self.assertEqual(split_spread_image(image, "ltr"), [image])
