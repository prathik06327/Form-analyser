import type { PoseKeypoint } from "@/types/analysis";

interface PoseDetectionOverlayProps {
  keypoints: PoseKeypoint[];
  active?: boolean;
}

const CHAIN: Array<[PoseKeypoint["name"], PoseKeypoint["name"]]> = [
  ["shoulder", "elbow"],
  ["elbow", "wrist"],
];

const LABELS: Record<PoseKeypoint["name"], string> = {
  shoulder: "Shoulder",
  elbow: "Elbow",
  wrist: "Wrist",
  hip: "Hip",
};

function findPoint(keypoints: PoseKeypoint[], name: PoseKeypoint["name"]) {
  return keypoints.find((k) => k.name === name);
}

export default function PoseDetectionOverlay({ keypoints, active = true }: PoseDetectionOverlayProps) {
  if (!active) return null;

  const shoulder = findPoint(keypoints, "shoulder");
  const hip = findPoint(keypoints, "hip");

  return (
    <div className="pointer-events-none absolute inset-0" aria-hidden>
      {/* Skeleton connective lines — separate SVG layer, mildly non-uniform scaling is acceptable for a stylized overlay */}
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
        {shoulder && hip && (
          <line
            x1={shoulder.x * 100}
            y1={shoulder.y * 100}
            x2={hip.x * 100}
            y2={hip.y * 100}
            stroke="var(--text-muted)"
            strokeWidth={0.5}
            strokeDasharray="2 2"
            opacity={0.5}
          />
        )}
        {CHAIN.map(([from, to]) => {
          const a = findPoint(keypoints, from);
          const b = findPoint(keypoints, to);
          if (!a || !b) return null;
          return (
            <line
              key={`${from}-${to}`}
              x1={a.x * 100}
              y1={a.y * 100}
              x2={b.x * 100}
              y2={b.y * 100}
              stroke="var(--accent-cyan)"
              strokeWidth={0.7}
              strokeLinecap="round"
              style={{ filter: "drop-shadow(0 0 2px rgba(34,229,201,0.7))" }}
            />
          );
        })}
      </svg>

      {/* Joints — plain HTML dots so they stay perfectly circular regardless of frame aspect ratio */}
      {keypoints.map((point) => (
        <div
          key={point.name}
          className="absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center"
          style={{ left: `${point.x * 100}%`, top: `${point.y * 100}%` }}
        >
          <span className="mb-1 whitespace-nowrap rounded bg-black/50 px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wide text-accent-cyan">
            {LABELS[point.name]}
          </span>
          <span className="relative flex size-3 items-center justify-center">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-accent-cyan opacity-30" />
            <span className="relative inline-flex size-2.5 rounded-full border-2 border-accent-cyan bg-[#0a0b0f] shadow-[0_0_6px_rgba(34,229,201,0.8)]" />
          </span>
        </div>
      ))}
    </div>
  );
}
