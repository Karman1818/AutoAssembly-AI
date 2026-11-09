import unittest
from backend.services.assembly_documents import (
    _safe_filename,
    _wrap_text,
    _dimensions,
    _part_kind,
    _part_area_weight,
    _part_fill,
    _panel_points,
    _connector_points,
    _normalize_card_size,
    _layout_cards,
    _svg_polygon,
    _svg_text,
    ImageColorHelper,
)


class TestAssemblyDocuments(unittest.TestCase):
    def test_safe_filename(self):
        self.assertEqual(_safe_filename("step-123_abc.step"), "step-123_abc_step")
        self.assertEqual(_safe_filename("invalid/path\\name!"), "invalid_path_name_")

    def test_wrap_text(self):
        text = "This is a short test sentence for wrapping text."
        wrapped = _wrap_text(text, width=20)
        self.assertGreater(len(wrapped), 1)
        self.assertTrue(all(len(line) <= 25 for line in wrapped))

    def test_dimensions(self):
        part = {"dimensions": [10.0, 20.0, 30.0]}
        self.assertEqual(_dimensions(part), (10.0, 20.0, 30.0))

        empty_part = {}
        self.assertEqual(_dimensions(empty_part), (0.0, 0.0, 0.0))

    def test_part_kind(self):
        self.assertEqual(_part_kind({"type": "panel"}), "panel")
        self.assertEqual(_part_kind({}), "other")

    def test_part_area_weight(self):
        panel = {"type": "panel", "dimensions": [5.0, 200.0, 300.0]}
        connector = {"type": "connector", "dimensions": [10.0, 10.0, 10.0], "quantity": 4}
        self.assertGreater(_part_area_weight(panel), _part_area_weight(connector))

    def test_part_fill(self):
        self.assertEqual(_part_fill("panel", highlight=False), "#f4a261")
        self.assertEqual(_part_fill("connector", highlight=False), "#2a9d8f")
        self.assertEqual(_part_fill("panel", highlight=True), "#e76f51")

    def test_shape_points(self):
        panel_pts = _panel_points(100.0, 50.0, 10.0, 20.0)
        self.assertEqual(len(panel_pts), 4)

        connector_pts = _connector_points(40.0, 40.0, 10.0, 10.0)
        self.assertEqual(len(connector_pts), 6)

    def test_normalize_card_size(self):
        part = {"type": "panel", "dimensions": [10.0, 100.0, 200.0]}
        w, h = _normalize_card_size(part)
        self.assertGreater(w, 0)
        self.assertGreater(h, 0)

    def test_layout_cards(self):
        parts = [
            {"id": f"p_{i}", "type": "panel", "dimensions": [10, 50, 100]}
            for i in range(5)
        ]
        placements = _layout_cards(parts, start_x=10, start_y=20, cols=2, gap_x=100, gap_y=80)
        self.assertEqual(len(placements), 5)
        self.assertEqual(placements[0]["x"], 10)
        self.assertEqual(placements[1]["x"], 110)

    def test_svg_helpers(self):
        poly = _svg_polygon([(0, 0), (10, 0), (10, 10)], "#ffffff", opacity=1.0)
        self.assertIn("<polygon", poly)
        self.assertIn('points="0.0,0.0 10.0,0.0 10.0,10.0"', poly)

        txt = _svg_text(10, 20, "Step 1 & 2 <Test>", 18)
        self.assertIn("<text", txt)
        self.assertIn("Step 1 &amp; 2 &lt;Test&gt;", txt)

    def test_image_color_helper(self):
        rgba = ImageColorHelper.hex_with_alpha("#ff8800", 0.5)
        self.assertEqual(rgba[0], 255)
        self.assertEqual(rgba[1], 136)
        self.assertEqual(rgba[2], 0)
        self.assertAlmostEqual(rgba[3], 127, delta=1)


if __name__ == "__main__":
    unittest.main()
