import LiveCameraView from "@/components/camera/LiveCameraView";
import RealTimeFeedbackToast, { type FeedbackToastData } from "@/components/ai/RealTimeFeedbackToast";
import WorkoutControls from "@/components/dashboard/WorkoutControls";
import type { CurlStatus, PoseKeypoint, SessionStatus } from "@/types/analysis";

interface LiveCameraModeProps {
  sessionStatus: SessionStatus;
  curlStatus: CurlStatus;
  keypoints: PoseKeypoint[];
  toasts: FeedbackToastData[];
  onDismissToast: (id: string) => void;
  onStart: () => void;
  onPause: () => void;
  onReset: () => void;
}

/**
 * Wraps the existing camera UI (unchanged) so it can be swapped in and out
 * as one of two exercise input modes, alongside VideoUpload. Camera frames
 * are never sent anywhere — this stays mock/placeholder until YOLO and the
 * FastAPI frame pipeline exist.
 */
export default function LiveCameraMode({
  sessionStatus,
  curlStatus,
  keypoints,
  toasts,
  onDismissToast,
  onStart,
  onPause,
  onReset,
}: LiveCameraModeProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="relative">
        <LiveCameraView sessionStatus={sessionStatus} curlStatus={curlStatus} keypoints={keypoints} />
        <RealTimeFeedbackToast toasts={toasts} onDismiss={onDismissToast} />
      </div>
      <WorkoutControls status={sessionStatus} onStart={onStart} onPause={onPause} onReset={onReset} />
    </div>
  );
}
