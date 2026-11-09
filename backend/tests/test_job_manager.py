import unittest
from backend.services.job_manager import JobManager


class TestJobManager(unittest.TestCase):
    def test_create_and_update_job(self):
        jm = JobManager()
        job_id = "test-job-123"
        jm.create_job(job_id)

        self.assertIn(job_id, jm.jobs)
        self.assertEqual(jm.jobs[job_id]["status"], "processing")
        self.assertEqual(jm.jobs[job_id]["progress"], 0)

        coro = jm.update_job(job_id, "processing", 50, "Halfway there")
        try:
            coro.send(None)
        except StopIteration:
            pass
        self.assertEqual(jm.jobs[job_id]["progress"], 50)
        self.assertEqual(jm.jobs[job_id]["message"], "Halfway there")

        coro = jm.update_job(job_id, "completed", 100, "Done", "/files/model.glb")
        try:
            coro.send(None)
        except StopIteration:
            pass
        self.assertEqual(jm.jobs[job_id]["status"], "completed")
        self.assertEqual(jm.jobs[job_id]["result_model_url"], "/files/model.glb")

        # Verify queue has the updates
        queue = jm.jobs[job_id]["queue"]
        self.assertEqual(queue.qsize(), 2)
        item1 = queue.get_nowait()
        self.assertEqual(item1["progress"], 50)
        item2 = queue.get_nowait()
        self.assertEqual(item2["status"], "completed")

    def test_update_nonexistent_job(self):
        jm = JobManager()
        coro = jm.update_job("nonexistent", "processing", 10, "msg")
        try:
            coro.send(None)
        except StopIteration:
            pass


if __name__ == "__main__":
    unittest.main()
