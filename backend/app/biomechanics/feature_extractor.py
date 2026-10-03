"""Collect biomechanics module outputs into a single structured payload."""

from __future__ import annotations


class FeatureExtractor:
    """Organize module outputs without performing calculations."""

    def extract(
        self,
        angle_data: dict[str, float | None],
        rom_data: dict[str, object],
        arm_data: dict[str, object],
        torso_data: dict[str, object],
    ) -> dict[str, object]:
        """Return one combined biomechanics dictionary."""

        return {
            "left_elbow_angle": angle_data.get("left_elbow_angle"),
            "right_elbow_angle": angle_data.get("right_elbow_angle"),
            "left_shoulder_angle": angle_data.get("left_shoulder_angle"),
            "right_shoulder_angle": angle_data.get("right_shoulder_angle"),
            "range_of_motion": rom_data.get("range_of_motion"),
            "min_elbow_angle": rom_data.get("min_angle"),
            "max_elbow_angle": rom_data.get("max_angle"),
            "active_rom_side": rom_data.get("active_side"),
            "torso_angle": torso_data.get("torso_angle"),
            "body_sway": torso_data.get("body_sway"),
            "body_lean": torso_data.get("body_lean"),
            "movement_direction": arm_data.get("movement_direction"),
            "active_arm_side": arm_data.get("active_side"),
            "arm_motion": {
                "left": arm_data.get("left"),
                "right": arm_data.get("right"),
            },
            "torso_details": torso_data,
            "rom_details": rom_data,
        }