"use client";

import { Bar, BarChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import type { RepAnalysis } from "@/types/analysis";
import { BarChart3 } from "lucide-react";

interface RepConsistencyChartProps {
  reps: RepAnalysis[];
}

interface TooltipPayloadItem {
  value: number;
  payload: { repNumber: number; tempo: number };
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayloadItem[] }) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  return (
    <div className="rounded-lg border border-hairline-strong bg-[#14151a] px-3 py-2 text-xs shadow-xl">
      <p className="font-semibold text-text-primary">Rep {point.repNumber}</p>
      <p className="mt-0.5 text-text-secondary">
        Tempo: <span className="font-semibold text-series-1">{point.tempo}s</span>
      </p>
    </div>
  );
}

export default function RepConsistencyChart({ reps }: RepConsistencyChartProps) {
  // Reps without a measured tempo are omitted rather than plotted as zero.
  const data = reps
    .filter((r): r is typeof r & { tempo: number } => r.tempo !== null)
    .map((r) => ({ repNumber: r.repNumber, tempo: r.tempo }));
  const avgTempo = data.length ? Number((data.reduce((sum, d) => sum + d.tempo, 0) / data.length).toFixed(2)) : 0;

  return (
    <GlassCard>
      <div className="flex items-center justify-between">
        <SectionLabel icon={<BarChart3 className="size-3.5" />}>Rep Consistency</SectionLabel>
        <span className="text-xs text-text-muted">
          Avg <span className="font-semibold text-text-secondary">{avgTempo}s</span>
        </span>
      </div>
      <div className="relative mt-4 h-64 w-full">
        {data.length === 0 && (
          <div className="absolute inset-0 z-10 flex items-center justify-center text-sm text-text-muted">
            No rep data yet — start analysis to begin.
          </div>
        )}
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
            <XAxis
              dataKey="repNumber"
              tick={{ fill: "var(--text-muted)", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "var(--chart-axis)" }}
              label={{ value: "Rep Number", position: "insideBottom", offset: -4, fill: "var(--text-muted)", fontSize: 11 }}
            />
            <YAxis
              tick={{ fill: "var(--text-muted)", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              width={44}
              unit="s"
            />
            <ReferenceLine y={avgTempo} stroke="var(--border-hairline-strong)" strokeDasharray="4 4" />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
            <Bar dataKey="tempo" fill="var(--series-1)" radius={[3, 3, 0, 0]} maxBarSize={22} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
}
