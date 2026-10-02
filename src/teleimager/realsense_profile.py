"""Explicit, opt-in capture profiles for RealSense cameras.

The USB2 profile deliberately keeps a decoded BGR stream because it is the
format used by ``RealSenseCamera``.  It lowers both RealSense cameras to the
same 640x480@6 profile rather than cropping, so optical FOV is unchanged.
"""
from __future__ import annotations

import copy
from typing import Any, Mapping, cast

NORMAL_PROFILE = "normal"
USB2_PROFILE = "usb2"
_PROFILE_ALIASES = {"low-bandwidth": USB2_PROFILE, "low_bandwidth": USB2_PROFILE}
USB2_IMAGE_SHAPE = [480, 640]
USB2_FPS = 6


def normalize_profile(profile: str | None) -> str:
    """Return a supported profile name, rejecting unsafe implicit fallbacks."""
    value = (profile or NORMAL_PROFILE).strip().lower()
    value = _PROFILE_ALIASES.get(value, value)
    if value not in (NORMAL_PROFILE, USB2_PROFILE):
        raise ValueError(f"unsupported RealSense profile {profile!r}; use normal|usb2|low-bandwidth")
    return value


def apply_realsense_profile(cam_config: Mapping[str, Any], profile: str | None) -> dict[str, Any]:
    """Copy a camera config and apply an explicit profile to enabled RealSense cameras."""
    result = cast(dict[str, Any], copy.deepcopy(cam_config))
    if normalize_profile(profile) != USB2_PROFILE:
        return result
    for camera in result.values():
        if not isinstance(camera, dict) or str(camera.get("type", "")).lower() != "realsense":
            continue
        camera["image_shape"] = list(USB2_IMAGE_SHAPE)
        camera["fps"] = USB2_FPS
    return result
