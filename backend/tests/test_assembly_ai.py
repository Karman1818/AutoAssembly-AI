import unittest
from backend.services.assembly_ai import (
    _part_sort_key,
    build_assembly_prompt,
    _strip_json_payload,
    _sanitize_steps,
    _merge_missing_parts,
    _compress_steps_to_limit,
    _heuristic_steps,
    _is_configured_api_key,
)


class TestAssemblyAI(unittest.TestCase):
    def setUp(self):
        self.sample_parts = [
            {
                "id": "part_0",
                "label": "Panel 1",
                "type": "panel",
                "quantity": 2,
                "dimensions": [15.0, 400.0, 600.0],
                "volume": 3600000.0,
            },
            {
                "id": "part_1",
                "label": "Connector 2",
                "type": "connector",
                "quantity": 8,
                "dimensions": [10.0, 10.0, 20.0],
                "volume": 2000.0,
            },
            {
                "id": "part_2",
                "label": "Part 3",
                "type": "other",
                "quantity": 1,
                "dimensions": [50.0, 50.0, 100.0],
                "volume": 250000.0,
            },
        ]
        self.parts_map = {p["id"]: p for p in self.sample_parts}

    def test_is_configured_api_key(self):
        self.assertFalse(_is_configured_api_key(None))
        self.assertFalse(_is_configured_api_key(""))
        self.assertFalse(_is_configured_api_key("   "))
        self.assertFalse(_is_configured_api_key("your_gemini_api_key_here"))
        self.assertFalse(_is_configured_api_key("placeholder_key"))
        self.assertTrue(_is_configured_api_key("AIzaSyB1234567890abcdef"))

    def test_part_sort_key(self):
        sorted_parts = sorted(self.sample_parts, key=_part_sort_key)
        self.assertEqual(sorted_parts[0]["type"], "panel")
        self.assertEqual(sorted_parts[1]["type"], "other")
        self.assertEqual(sorted_parts[2]["type"], "connector")

    def test_build_assembly_prompt(self):
        prompt = build_assembly_prompt(self.sample_parts)
        self.assertIn("expert furniture assembly planner", prompt)
        self.assertIn("part_0", prompt)
        self.assertIn("part_1", prompt)
        self.assertIn("RULES:", prompt)

    def test_strip_json_payload(self):
        raw_fenced = '```json\n{"title": "Test Instructions", "steps": []}\n```'
        cleaned = _strip_json_payload(raw_fenced)
        self.assertEqual(cleaned, '{"title": "Test Instructions", "steps": []}')

        plain_json = '{"title": "Test Instructions"}'
        self.assertEqual(_strip_json_payload(plain_json), plain_json)

    def test_sanitize_steps(self):
        raw_steps = [
            {
                "title": "First Step",
                "description": "Place base panels.",
                "parts_used": [
                    {"part_id": "part_0", "quantity_in_step": 2},
                    {"part_id": "nonexistent_part", "quantity_in_step": 1},
                ],
            },
            {
                "title": "Duplicate Step",
                "description": "Reuse part_0.",
                "parts_used": [{"part_id": "part_0", "quantity_in_step": 1}],
            },
        ]
        sanitized = _sanitize_steps(raw_steps, self.parts_map)
        self.assertEqual(len(sanitized), 1)
        self.assertEqual(sanitized[0]["step_number"], 1)
        self.assertEqual(len(sanitized[0]["parts_used"]), 1)
        self.assertEqual(sanitized[0]["parts_used"][0]["part_id"], "part_0")

    def test_merge_missing_parts(self):
        initial_steps = [
            {
                "step_number": 1,
                "title": "Step 1",
                "description": "Place panels",
                "parts_used": [{"part_id": "part_0", "quantity_in_step": 2}],
            }
        ]
        merged = _merge_missing_parts(initial_steps, self.parts_map)
        all_parts_used = {
            item["part_id"] for step in merged for item in step["parts_used"]
        }
        self.assertEqual(all_parts_used, {"part_0", "part_1", "part_2"})

    def test_compress_steps_to_limit(self):
        many_steps = [
            {
                "step_number": i,
                "title": f"Step {i}",
                "description": f"Instruction {i}.",
                "parts_used": [{"part_id": "part_0", "quantity_in_step": 1}],
            }
            for i in range(1, 15)
        ]
        compressed = _compress_steps_to_limit(many_steps, max_steps=10)
        self.assertEqual(len(compressed), 10)
        self.assertEqual(compressed[-1]["step_number"], 10)

    def test_heuristic_steps(self):
        steps = _heuristic_steps(self.sample_parts)
        self.assertGreaterEqual(len(steps), 1)
        all_part_ids = {
            item["part_id"] for step in steps for item in step["parts_used"]
        }
        self.assertIn("part_0", all_part_ids)
        self.assertIn("part_1", all_part_ids)
        self.assertIn("part_2", all_part_ids)


if __name__ == "__main__":
    unittest.main()
