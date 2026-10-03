"use client";

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import type { RepAnalysis } from "@/types/analysis";
import { TrendingUp } from "lucide-react";

interface PerformanceChartProps {
  reps: RepAnalysis[];
}

interface TooltipPayloadItem {
  value: number;
  payload: { repNumber: number; formScore: number };
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayloadItem[] }) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  return (
    <div className="rounded-lg border border-hairline-strong bg-[#14151a] px-3 py-2 text-xs shadow-xl">
      <p className="font-semibold text-text-primary">Rep {point.repNumber}</p>
      <p className="mt-0.5 text-text-secondary">
        Form Score: <span className="font-semibold text-series-1">{point.formScore}</span>
      </p>
    </div>
  );
}

export default function PerformanceChart({ reps }: PerformanceChartProps) {
  const data = reps.map((r) => ({ repNumber: r.repNumber, formScore: r.formScore }));

  return (
    <GlassCard>
      <SectionLabel icon={<TrendingUp className="size-3.5" />}>Form Score by Rep</SectionLabel>
      <div className="relative mt-4 h-64 w-full">
        {data.length === 0 && (
          <div className="absolute inset-0 z-10 flex items-center justify-center text-sm text-text-muted">
            No rep data yet — start analysis to begin.
          </div>
        )}
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--chart-grid)" strokeDasharray="0" />
            <XAxis
              dataKey="repNumber"
              tick={{ fill: "var(--text-muted)", fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: "var(--chart-axis)" }}
              label={{ value: "Rep Number", position: "insideBottom", offset: -4, fill: "var(--text-muted)", fontSize: 11 }}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: "var(--text-muted)", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              width={40}
            />
            <Tooltip content={<ChartTooltip />} cursor={{ stroke: "var(--border-hairline-strong)", strokeWidth: 1 }} />
            <Line
              type="monotone"
              dataKey="formScore"
              stroke="var(--series-1)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "var(--series-1)", stroke: "var(--bg-surface)", strokeWidth: 2 }}
              strokeLinecap="round"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
}
