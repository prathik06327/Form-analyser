"""Pose detection service for Phase 1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO


KEYPOINT_NAMES = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
]

DEBUG_KEYPOINT_NAMES = [
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
]


@dataclass(slots=True)
class Keypoint:
    """A single pose keypoint with coordinates and confidence."""

    name: str
    x: float
    y: float
    confidence: float


@dataclass(slots=True)
class PoseDetectionResult:
    """Structured pose detection output used by the application."""

    annotated_frame: np.ndarray
    has_person: bool
    keypoints: dict[str, Keypoint]
    confidences: dict[str, float]
    message: str = ""

    def plot(self) -> np.ndarray:
        """Preserve compatibility with the existing webcam test script."""

        return self.annotated_frame


class PoseService:
    """Encapsulates YOLO pose inference and keypoint extraction."""

    def __init__(self, model_path: str | Path = "yolo11n-pose.pt") -> None:
        model_file = Path(model_path)
        if not model_file.exists():
            raise FileNotFoundError(f"Pose model not found: {model_file}")

        self.model = YOLO(str(model_file))

    def detect_pose(self, frame: np.ndarray) -> PoseDetectionResult:
        """Run pose estimation on a single OpenCV frame."""

        if frame is None or frame.size == 0:
            raise ValueError("frame must be a valid OpenCV image")

        results = self.model(frame, verbose=False)
        result = results[0] if results else None

        if result is None or not self._has_person(result):
            annotated_frame = frame.copy()
            self._draw_message(annotated_frame, "No person detected")
            return PoseDetectionResult(
                annotated_frame=annotated_frame,
                has_person=False,
                keypoints={},
                confidences={},
                message="No person detected",
            )

        keypoints = self.extract_keypoints(result)
        confidences = self.extract_confidence(result)

        annotated_frame = result.plot()
        return PoseDetectionResult(
            annotated_frame=annotated_frame,
            has_person=True,
            keypoints=keypoints,
            confidences=confidences,
            message="",
        )

    def extract_keypoints(self, result: Any) -> dict[str, Keypoint]:
        """Extract the first person's raw keypoint coordinates."""

        keypoints = getattr(result, "keypoints", None)
        if keypoints is None:
            return {}

        xy = getattr(keypoints, "xy", None)
        if xy is None:
            return {}

        xy_array = self._to_numpy(xy)
        if xy_array is None or xy_array.size == 0:
            return {}

        xy_array = np.asarray(xy_array)
        if xy_array.ndim == 3:
            xy_array = xy_array[0]

        confidence_values = self._to_numpy(getattr(keypoints, "conf", None))
        if confidence_values is not None:
            confidence_values = np.asarray(confidence_values)
            if confidence_values.ndim == 2:
                confidence_values = confidence_values[0]

        extracted_keypoints: dict[str, Keypoint] = {}
        for index, name in enumerate(KEYPOINT_NAMES):
            if index >= len(xy_array):
                break

            x_value = float(xy_array[index][0])
            y_value = float(xy_array[index][1])
            confidence = 0.0

            if confidence_values is not None and index < len(confidence_values):
                confidence = float(confidence_values[index])

            extracted_keypoints[name] = Keypoint(
                name=name,
                x=x_value,
                y=y_value,
                confidence=confidence,
            )

        return extracted_keypoints

    def extract_confidence(self, result: Any) -> dict[str, float]:
        """Extract confidence values for the first person's keypoints."""

        keypoints = getattr(result, "keypoints", None)
        if keypoints is None:
            return {}

        confidence_values = self._to_numpy(getattr(keypoints, "conf", None))
        if confidence_values is None or confidence_values.size == 0:
            return {}

        confidence_values = np.asarray(confidence_values)
        if confidence_values.ndim == 2:
            confidence_values = confidence_values[0]

        extracted_confidence: dict[str, float] = {}
        for index, name in enumerate(KEYPOINT_NAMES):
            if index >= len(confidence_values):
                break
            extracted_confidence[name] = float(confidence_values[index])

        return extracted_confidence

    def _has_person(self, result: Any) -> bool:
        """Check whether YOLO detected at least one person."""

        boxes = getattr(result, "boxes", None)
        if boxes is not None:
            try:
                return len(boxes) > 0
            except TypeError:
                pass

        keypoints = getattr(result, "keypoints", None)
        if keypoints is None:
            return False

        xy = getattr(keypoints, "xy", None)
        if xy is None:
            return False

        try:
            return len(xy) > 0 and len(xy[0]) > 0
        except TypeError:
            return False

    def _draw_message(self, frame: np.ndarray, message: str) -> None:
        """Overlay a status message on the provided frame."""

        cv2.putText(
            frame,
            message,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )

    def _to_numpy(self, value: Any) -> np.ndarray | None:
        """Convert tensors and array-like values to NumPy arrays."""

        if value is None:
            return None

        if hasattr(value, "detach"):
            value = value.detach()

        if hasattr(value, "cpu"):
            value = value.cpu()

        if hasattr(value, "numpy"):
            return value.numpy()

        return np.asarray(value)