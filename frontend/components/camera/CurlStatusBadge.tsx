import StatusBadge from "@/components/ui/StatusBadge";
import { CURL_STATUS_TONE } from "@/lib/utils";
import type { CurlStatus } from "@/types/analysis";

interface CurlStatusBadgeProps {
  status: CurlStatus;
  className?: string;
}

export default function CurlStatusBadge({ status, className }: CurlStatusBadgeProps) {
  return (
    <StatusBadge tone={CURL_STATUS_TONE[status]} pulse={status === "CURLING"} className={className}>
      {status}
    </StatusBadge>
  );
}
