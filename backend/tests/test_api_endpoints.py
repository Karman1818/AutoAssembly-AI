import unittest
from fastapi import HTTPException
from backend.main import read_root
from backend.api.endpoints.assembly import (
    generate_instructions,
    get_instructions,
    get_instructions_pdf,
)


class TestApiEndpoints(unittest.TestCase):
    def test_root_endpoint(self):
        res = read_root()
        self.assertEqual(res, {"message": "CAD Assembly Generator API is running!"})

    def test_get_instructions_not_found(self):
        coro = get_instructions("nonexistent-job-id")
        with self.assertRaises(HTTPException) as ctx:
            try:
                coro.send(None)
            finally:
                coro.close()
        self.assertEqual(ctx.exception.status_code, 404)

    def test_get_pdf_not_found(self):
        coro = get_instructions_pdf("nonexistent-job-id")
        with self.assertRaises(HTTPException) as ctx:
            try:
                coro.send(None)
            finally:
                coro.close()
        self.assertEqual(ctx.exception.status_code, 404)

    def test_generate_instructions_missing_metadata(self):
        coro = generate_instructions("nonexistent-job-id")
        with self.assertRaises(HTTPException) as ctx:
            try:
                coro.send(None)
            finally:
                coro.close()
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("Parts metadata not found", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()
