import copy
import unittest

from teleimager.realsense_profile import apply_realsense_profile, normalize_profile


class RealSenseProfileTests(unittest.TestCase):
    def test_usb2_changes_each_enabled_realsense_without_disabling_streams(self):
        config = {
            "head_camera": {
                "type": "realsense", "enable_zmq": True, "image_shape": [720, 1280], "fps": 15,
            },
            "left_wrist_camera": {
                "type": "realsense", "enable_zmq": True, "image_shape": [720, 1280], "fps": 15,
            },
            "right_wrist_camera": {"type": "uvc", "enable_zmq": True, "image_shape": [480, 640], "fps": 30},
        }

        result = apply_realsense_profile(config, "usb2")

        self.assertEqual([480, 640], result["head_camera"]["image_shape"])
        self.assertEqual(6, result["head_camera"]["fps"])
        self.assertEqual([480, 640], result["left_wrist_camera"]["image_shape"])
        self.assertEqual(6, result["left_wrist_camera"]["fps"])
        self.assertTrue(result["head_camera"]["enable_zmq"])
        self.assertTrue(result["left_wrist_camera"]["enable_zmq"])
        self.assertEqual([480, 640], result["right_wrist_camera"]["image_shape"])
        self.assertEqual(30, result["right_wrist_camera"]["fps"])
        self.assertEqual([720, 1280], config["head_camera"]["image_shape"])

    def test_low_bandwidth_is_usb2_alias_and_normal_is_noop_copy(self):
        config = {"head_camera": {"type": "realsense", "image_shape": [720, 1280], "fps": 15}}

        self.assertEqual("usb2", normalize_profile("low-bandwidth"))
        self.assertEqual(apply_realsense_profile(config, "usb2"), apply_realsense_profile(config, "low-bandwidth"))
        normal = apply_realsense_profile(config, "normal")
        self.assertEqual(config, normal)
        self.assertIsNot(config, normal)

    def test_unknown_profile_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "normal|usb2"):
            normalize_profile("turbo")


if __name__ == "__main__":
    unittest.main()
