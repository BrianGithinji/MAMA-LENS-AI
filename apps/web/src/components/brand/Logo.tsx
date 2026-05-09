/**
 * MAMA-LENS AI — Logo Component
 * Uses the official MAMA-LENS AI PNG logo as-is, at reduced sizes.
 */

import logoPng from "../../assets/logo.png";
import { clsx } from "clsx";

interface LogoProps {
  variant?: "full" | "compact" | "icon";
  /** Override the default width in pixels */
  width?: number;
  /** Invert colours for use on dark/coloured backgrounds */
  inverted?: boolean;
  className?: string;
}

const DEFAULT_WIDTHS: Record<NonNullable<LogoProps["variant"]>, number> = {
  full:    160,
  compact: 100,
  icon:     40,
};

export default function Logo({
  variant = "full",
  width,
  inverted = false,
  className,
}: LogoProps) {
  const w = width ?? DEFAULT_WIDTHS[variant];

  return (
    <img
      src={logoPng}
      alt="MAMA-LENS AI"
      width={w}
      style={{ width: w, height: "auto", display: "block" }}
      className={clsx(
        "select-none flex-shrink-0",
        inverted && "brightness-0 invert",   // CSS filter to make it white on dark bg
        className
      )}
      draggable={false}
    />
  );
}
