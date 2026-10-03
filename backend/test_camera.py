import cv2

from app.assessment.assessment_engine import AssessmentEngine
from app.biomechanics.biomechanics_engine import BiomechanicsEngine
from app.repetition.repetition_engine import RepetitionEngine
from app.scoring.scoring_engine import ScoringEngine
from app.services.pose_service import PoseService


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


def main():
    # Create the pose service and load YOLO11 Pose.
    pose_service = PoseService()
    biomechanics_engine = BiomechanicsEngine()
    repetition_engine = RepetitionEngine()
    assessment_engine = AssessmentEngine()
    scoring_engine = ScoringEngine()

    # Open the default webcam.
    camera = cv2.VideoCapture(0)

    # Check whether the webcam opened successfully.
    if not camera.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Webcam started.")
    print("Press Q to exit.")

    frame_number = 0

    while True:
        # Read one frame from the webcam.
        success, frame = camera.read()

        # Stop if OpenCV cannot read a frame.
        if not success:
            print("Error: Could not read frame.")
            break

        frame_number += 1

        # Run YOLO pose estimation.
        result = pose_service.detect_pose(frame)

        # Feed extracted keypoints into the Phase 2 biomechanics engine.
        measurements = biomechanics_engine.process_frame(result.keypoints)
        repetition_info = repetition_engine.process_frame(measurements, frame_number=frame_number)
        print(format_biomechanics_output(frame_number, measurements))
        print(format_repetition_output(frame_number, repetition_info))

        completed_rep = repetition_info.get("completed_rep")
        if completed_rep is not None:
            print("Rep Completed")
            assessment_result = assessment_engine.assess_rep_dict(completed_rep)
            print(format_assessment_output(assessment_result))
            score_result = scoring_engine.process_assessment(assessment_result)
            print(format_scoring_output(score_result))

        # Draw YOLO's detected skeleton and keypoints.
        annotated_frame = result.plot()

        # Display the result.
        cv2.imshow("Bicep Curl Pose Detection", annotated_frame)

        # Exit when the Q key is pressed.
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the webcam.
    camera.release()

    # Close all OpenCV windows.
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()