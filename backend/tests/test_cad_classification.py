import unittest
from backend.services.cad_pipeline import (
    _dims_match,
    _classify_part,
    _part_label,
    _group_key,
    _should_group,
)


class TestCadClassification(unittest.TestCase):
    def test_dims_match(self):
        self.assertTrue(_dims_match(10.0, 10.0))
        self.assertTrue(_dims_match(10.0, 10.5, tol=0.10))
        self.assertFalse(_dims_match(10.0, 15.0, tol=0.10))

    def test_classify_connector(self):
        part_type, reason = _classify_part((20.0, 20.0, 30.0), 5000.0)
        self.assertEqual(part_type, "connector")
        self.assertIn("connector", reason)

    def test_classify_panel(self):
        part_type, reason = _classify_part((5.0, 200.0, 300.0), 300000.0)
        self.assertEqual(part_type, "panel")
        self.assertIn("plate", reason)

    def test_classify_other(self):
        part_type, reason = _classify_part((80.0, 80.0, 80.0), 512000.0)
        self.assertEqual(part_type, "other")
        self.assertIn("solid", reason)

    def test_part_label(self):
        self.assertEqual(_part_label("panel", 0), "Panel 1")
        self.assertEqual(_part_label("connector", 2), "Connector 3")
        self.assertEqual(_part_label("other", 1), "Part 2")
        self.assertEqual(_part_label("unknown", 0), "Part 1")

    def test_group_key(self):
        key1 = _group_key((10.2, 5.1, 20.4), 1040.4)
        key2 = _group_key((20.4, 10.2, 5.1), 1040.4)
        self.assertEqual(key1, key2)
        self.assertEqual(key1, (5, 10, 20, 1040))

    def test_should_group(self):
        self.assertTrue(_should_group("connector", (10.0, 10.0, 10.0), 1000.0))
        self.assertTrue(_should_group("other", (20.0, 30.0, 40.0), 5000.0))
        self.assertFalse(_should_group("panel", (10.0, 100.0, 200.0), 200000.0))


if __name__ == "__main__":
    unittest.main()
