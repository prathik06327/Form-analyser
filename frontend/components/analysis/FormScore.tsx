import GlassCard from "@/components/ui/GlassCard";
import SectionLabel from "@/components/ui/SectionLabel";
import CircularScoreGauge from "@/components/ui/CircularScoreGauge";
import { Target } from "lucide-react";

interface FormScoreProps {
  score: number;
  hasData?: boolean;
}

export default function FormScore({ score, hasData = true }: FormScoreProps) {
  return (
    <GlassCard className="flex flex-col items-center text-center">
      <SectionLabel icon={<Target className="size-3.5" />} className="self-start">
        Form Score
      </SectionLabel>
      <div className="mt-4">
        <CircularScoreGauge score={score} hasData={hasData} />
      </div>
    </GlassCard>
  );
}
