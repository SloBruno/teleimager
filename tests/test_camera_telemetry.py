import unittest

from teleimager.camera_telemetry import CameraTelemetry


class CameraTelemetryTests(unittest.TestCase):
    def test_snapshot_tracks_success_publish_error_and_age_without_resetting_frame_state(self):
        now = [100.0]
        telemetry = CameraTelemetry(clock=lambda: now[0])

        telemetry.capture_ok()
        telemetry.publish_ok()
        now[0] = 103.5
        telemetry.capture_error()
        snapshot = telemetry.snapshot()

        self.assertEqual(1, snapshot["capture_seq"])
        self.assertEqual(1, snapshot["publish_seq"])
        self.assertEqual(1, snapshot["capture_errors"])
        self.assertEqual(0, snapshot["publish_errors"])
        self.assertEqual(3.5, snapshot["capture_age_s"])
        self.assertEqual(3.5, snapshot["publish_age_s"])

    def test_age_is_none_before_first_success(self):
        telemetry = CameraTelemetry(clock=lambda: 10.0)
        telemetry.publish_error()
        snapshot = telemetry.snapshot()
        self.assertIsNone(snapshot["capture_age_s"])
        self.assertIsNone(snapshot["publish_age_s"])
        self.assertEqual(1, snapshot["publish_errors"])


if __name__ == "__main__":
    unittest.main()
