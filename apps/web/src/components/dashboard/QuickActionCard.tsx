/**
 * MAMA-LENS AI — Quick Action Card Component
 */

import { Link } from "react-router-dom";
import { LucideIcon } from "lucide-react";
import { clsx } from "clsx";

interface QuickActionCardProps {
  icon: LucideIcon;
  label: string;
  description: string;
  href: string;
  color: string;
  urgent?: boolean;
}

export default function QuickActionCard({
  icon: Icon,
  label,
  description,
  href,
  color,
  urgent = false,
}: QuickActionCardProps) {
  return (
    <Link
      to={href}
      className={clsx(
        "block bg-white rounded-3xl p-4 shadow-card hover:shadow-md transition-all active:scale-95",
        urgent && "ring-2 ring-emergency-400"
      )}
    >
      <div className={clsx("w-10 h-10 rounded-2xl flex items-center justify-center mb-3", color)}>
        <Icon className="w-5 h-5" />
      </div>
      <p className="font-semibold text-gray-900 text-sm leading-tight">{label}</p>
      <p className="text-gray-400 text-xs mt-0.5 leading-tight">{description}</p>
      {urgent && (
        <span className="inline-block mt-2 text-xs bg-emergency-100 text-emergency-600 px-2 py-0.5 rounded-full font-medium">
          Action needed
        </span>
      )}
    </Link>
  );
}
