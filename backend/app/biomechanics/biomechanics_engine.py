"""Controller for the Phase 2 biomechanics workflow."""

from __future__ import annotations

from typing import Mapping

from app.biomechanics.angle_calculator import AngleCalculator
from app.biomechanics.arm_tracker import ArmTracker
from app.biomechanics.feature_extractor import FeatureExtractor
from app.biomechanics.rom_analyzer import RangeOfMotionAnalyzer
from app.biomechanics.torso_tracker import TorsoTracker
from app.services.pose_service import Keypoint


class BiomechanicsEngine:
    """Coordinate all biomechanics measurements from pose keypoints."""

    def __init__(self, min_confidence: float = 0.3) -> None:
        self.min_confidence = min_confidence
        self.angle_calculator = AngleCalculator(min_confidence=min_confidence)
        self.rom_analyzer = RangeOfMotionAnalyzer()
        self.arm_tracker = ArmTracker()
        self.torso_tracker = TorsoTracker()
        self.feature_extractor = FeatureExtractor()

    def process_frame(
        self,
        keypoints: Mapping[str, Keypoint] | None,
    ) -> dict[str, object]:
        """Run the biomechanics pipeline for one frame of extracted keypoints."""

        keypoints = keypoints or {}

        angle_data = self.angle_calculator.calculate_joint_angles(keypoints, self.min_confidence)
        rom_data = self.rom_analyzer.update(
            left_angle=angle_data.get("left_elbow_angle"),
            right_angle=angle_data.get("right_elbow_angle"),
        )
        arm_data = self.arm_tracker.update(keypoints, self.min_confidence)
        torso_data = self.torso_tracker.update(keypoints, self.min_confidence)

        return self.feature_extractor.extract(angle_data, rom_data, arm_data, torso_data)

    def reset(self) -> None:
        """Reset all tracked biomechanics state."""

        self.rom_analyzer.reset()
        self.arm_tracker.reset()
        self.torso_tracker.reset()