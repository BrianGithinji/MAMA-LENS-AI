/**
 * MAMA-LENS AI — Logo Component
 * Uses the official MAMA-LENS AI PNG logo as-is, at reduced sizes.
 *
 * Variants:
 *   full    — larger logo for auth screens / splash (width ~160px)
 *   compact — medium logo for nav headers (width ~100px)
 *   icon    — small logo for avatars / badges (width ~40px)
 */

import logoPng from "../../assets/logo.png";
import { clsx } from "clsx";

interface LogoProps {
  variant?: "full" | "compact" | "icon";
  className?: string;
}

const WIDTHS: Record<NonNullable<LogoProps["variant"]>, number> = {
  full:    160,
  compact: 100,
  icon:     40,
};

export default function Logo({ variant = "full", className }: LogoProps) {
  const width = WIDTHS[variant];

  return (
    <img
      src={logoPng}
      alt="MAMA-LENS AI"
      width={width}
      style={{ width, height: "auto", display: "block" }}
      className={clsx("select-none flex-shrink-0", className)}
      draggable={false}
    />
  );
}
