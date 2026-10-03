"""Phase 1 video runner for bicep curl pose detection."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2

from app.assessment.assessment_engine import AssessmentEngine
from app.biomechanics.biomechanics_engine import BiomechanicsEngine
from app.repetition.repetition_engine import RepetitionEngine
from app.scoring.scoring_engine import ScoringEngine
from app.services.pose_service import DEBUG_KEYPOINT_NAMES, PoseService


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    default_video = Path(__file__).resolve().parent / "videos" / "bicep_curl.mp4"

    parser = argparse.ArgumentParser(
        description="Run YOLO11 pose detection on a video file."
    )
    parser.add_argument(
        "--video",
        type=Path,
        default=default_video,
        help="Path to the input video file.",
    )
    return parser.parse_args()


def overlay_text(frame, lines, origin=(20, 80), line_height=24):
    """Draw multiple lines of debug text on a frame."""

    x_position, y_position = origin
    for index, line in enumerate(lines):
        cv2.putText(
            frame,
            line,
            (x_position, y_position + (index * line_height)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )


def format_keypoint_line(name, keypoint, confidence_value):
    """Format a single keypoint debug line."""

    if keypoint is None:
        return f"{name}: not detected"

    return (
        f"{name}: x={keypoint.x:.1f}, y={keypoint.y:.1f}, "
        f"conf={confidence_value:.2f}"
    )


def format_biomechanics_output(frame_number, measurements):
    """Create a readable biomechanics debug message for console output."""

    def format_value(value, suffix=""):
        if value is None:
            return "n/a"
        if isinstance(value, (int, float)):
            return f"{value:.1f}{suffix}"
        return str(value)

    lines = [
        f"Frame {frame_number}",
        f"Left Elbow Angle : {format_value(measurements.get('left_elbow_angle'), '°')}",
        f"Right Elbow Angle: {format_value(measurements.get('right_elbow_angle'), '°')}",
        f"Range of Motion  : {format_value(measurements.get('range_of_motion'), '°')}",
        f"Torso Angle      : {format_value(measurements.get('torso_angle'), '°')}",
        f"Body Sway        : {format_value(measurements.get('body_sway'))}",
        f"Movement         : {format_value(measurements.get('movement_direction'))}",
    ]
    return "\n".join(lines)


def format_repetition_output(frame_number, repetition_info):
    """Create a readable repetition debug message for console output."""

    def format_value(value, suffix=""):
        if value is None:
            return "n/a"
        if isinstance(value, (int, float)):
            return f"{value:.1f}{suffix}"
        return str(value)

    lines = [
        f"Frame {frame_number}",
        f"Current State: {repetition_info.get('current_state', 'IDLE')}",
        f"Current Rep: {repetition_info.get('current_rep', 0)}",
        f"Total Reps: {repetition_info.get('total_reps', 0)}",
        f"Movement: {repetition_info.get('movement_direction', 'Stationary')}",
        f"Current Elbow Angle: {format_value(repetition_info.get('current_elbow_angle'), '°')}",
        f"Current ROM: {format_value(repetition_info.get('current_rom'), '°')}",
        f"Rep Progress: {format_value(repetition_info.get('rep_progress'), '%')}",
    ]
    return "\n".join(lines)


def format_assessment_output(assessment_result):
    """Create a readable assessment debug message for console output."""

    lines = [f"Rep {assessment_result.get('rep_number', 0)}", "Assessment"]
    assessment = assessment_result.get("assessment") or []

    if not assessment:
        lines.append("✓ Full Extension")
    else:
        for entry in assessment:
            lines.append(f"✗ {entry.get('mistake', 'Unknown Mistake')}")
            lines.append(f"Severity: {entry.get('severity', 'LOW')}")

    movement_quality = assessment_result.get("movement_quality") or {}
    lines.extend(
        [
            "Movement Quality",
            f"ROM: {movement_quality.get('rom', 'n/a')}°",
            f"Average Torso Lean: {movement_quality.get('average_torso_lean', 'n/a')}°",
            f"Average Body Sway: {movement_quality.get('average_body_sway', 'n/a')}",
            f"Tempo Consistency: {movement_quality.get('tempo_consistency', 'n/a')}",
        ]
    )
    return "\n".join(lines)


def format_scoring_output(score_result):
    """Create a readable scoring debug message for console output."""

    def format_number(value):
        try:
            return f"{float(value):.0f}"
        except (TypeError, ValueError):
            return "n/a"

    rep_score = score_result.get("rep_score") or {}
    session_score = score_result.get("session_score") or {}
    scores = rep_score.get("scores") or {}

    lines = [f"Rep {rep_score.get('rep_number', 0)}", "Scores"]
    lines.extend(
        [
            f"ROM: {format_number(scores.get('rom'))}",
            f"Tempo: {format_number(scores.get('tempo'))}",
            f"Stability: {format_number(scores.get('stability'))}",
            f"Body Control: {format_number(scores.get('body_control'))}",
            f"Elbow Control: {format_number(scores.get('elbow_control'))}",
            f"Overall Score: {format_number(rep_score.get('overall_score'))}",
            f"Grade: {rep_score.get('grade', 'Needs Improvement')}",
        ]
    )

    penalties = rep_score.get("penalties") or []
    lines.append("Penalties")
    if not penalties:
        lines.append("None")
    else:
        for penalty in penalties:
            lines.append(f"{penalty.get('reason', 'Unknown')} (-{penalty.get('amount', 0):.0f})")

    bonuses = rep_score.get("bonuses") or []
    lines.append("Bonuses")
    if not bonuses:
        lines.append("None")
    else:
        for bonus in bonuses:
            lines.append(f"{bonus.get('reason', 'Unknown')} (+{bonus.get('amount', 0):.0f})")

    lines.extend(
        [
            "Workout Summary",
            f"Total Reps: {session_score.get('total_reps', 0)}",
            f"Average Score: {format_number(session_score.get('average_rep_score'))}",
            f"Best Rep: {format_number(session_score.get('best_rep'))}",
            f"Worst Rep: {format_number(session_score.get('worst_rep'))}",
            f"Consistency Score: {format_number(session_score.get('consistency_score'))}",
            f"Workout Grade: {session_score.get('grade', 'Needs Improvement')}",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    """Open a video file, run pose detection, and display annotated frames."""

    args = parse_args()
    video_path = args.video

    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        return

    pose_service = PoseService()
    biomechanics_engine = BiomechanicsEngine()
    repetition_engine = RepetitionEngine()
    assessment_engine = AssessmentEngine()
    scoring_engine = ScoringEngine()
    capture = cv2.VideoCapture(str(video_path))

    if not capture.isOpened():
        print(f"Error: Could not open video file: {video_path}")
        return

    # Repetition timing must come from video time, not wall-clock time. Passing
    # the default wall-clock timestamp would make tempo/duration reflect how fast
    # this machine processed frames rather than how fast the lifter actually moved.
    fps = capture.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0 or fps != fps:  # 0/NaN for some codecs
        fps = 30.0

    print(f"Processing video: {video_path}")
    print("Press Q to exit.")

    frame_number = 0

    while True:
        frame_start_time = time.time()
        success, frame = capture.read()

        if not success:
            break

        frame_number += 1

        detection = pose_service.detect_pose(frame)
        measurements = biomechanics_engine.process_frame(detection.keypoints)
        repetition_info = repetition_engine.process_frame(
            measurements,
            frame_number=frame_number,
            timestamp=frame_number / fps,
        )
        output_frame = detection.plot()

        print(format_biomechanics_output(frame_number, measurements))
        print(format_repetition_output(frame_number, repetition_info))

        completed_rep = repetition_info.get("completed_rep")
        if completed_rep is not None:
            print("Rep Completed")
            assessment_result = assessment_engine.assess_rep_dict(completed_rep)
            print(format_assessment_output(assessment_result))
            score_result = scoring_engine.process_assessment(assessment_result)
            print(format_scoring_output(score_result))

        fps = 1.0 / max(time.time() - frame_start_time, 1e-6)

        cv2.putText(
            output_frame,
            f"FPS: {fps:.2f}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        if detection.has_person:
            keypoint_lines = []
            for name in DEBUG_KEYPOINT_NAMES:
                keypoint = detection.keypoints.get(name)
                confidence_value = detection.confidences.get(name, 0.0)
                keypoint_lines.append(
                    format_keypoint_line(name, keypoint, confidence_value)
                )

            overlay_text(output_frame, keypoint_lines)
        else:
            cv2.putText(
                output_frame,
                detection.message,
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )

        cv2.imshow("Bicep Curl Pose Detection", output_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()