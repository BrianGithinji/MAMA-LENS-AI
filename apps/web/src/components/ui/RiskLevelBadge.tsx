import { clsx } from "clsx";

interface RiskLevelBadgeProps {
  level: string;
  large?: boolean;
}

const RISK_CONFIG = {
  low: {
    label: "Low Risk",
    className: "bg-secondary-100 text-secondary-700 border-secondary-200",
  },
  moderate: {
    label: "Moderate Risk",
    className: "bg-warm-100 text-warm-700 border-warm-200",
  },
  high: {
    label: "High Risk",
    className: "bg-orange-100 text-orange-700 border-orange-200",
  },
  emergency: {
    label: "Emergency",
    className: "bg-emergency-100 text-emergency-700 border-emergency-200 animate-pulse",
  },
};

export default function RiskLevelBadge({ level, large = false }: RiskLevelBadgeProps) {
  const config = RISK_CONFIG[level as keyof typeof RISK_CONFIG] || RISK_CONFIG.low;

  return (
    <span
      className={clsx(
        "inline-flex items-center border rounded-full font-semibold",
        config.className,
        large ? "text-base px-4 py-2 mt-1" : "text-xs px-3 py-1"
      )}
    >
      {config.label}
    </span>
  );
}
