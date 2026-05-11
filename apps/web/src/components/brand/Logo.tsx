import logoPng from "../../assets/logo.png";
import { clsx } from "clsx";

interface LogoProps {
  variant?: "full" | "compact" | "icon";
  width?: number;
  inverted?: boolean;
  className?: string;
}

const DEFAULT_WIDTHS: Record<NonNullable<LogoProps["variant"]>, number> = {
  full:    160,
  compact: 100,
  icon:     40,
};

export default function Logo({ variant = "full", width, className }: LogoProps) {
  const w = width ?? DEFAULT_WIDTHS[variant];
  return (
    <img
      src={logoPng}
      alt="MAMA-LENS AI"
      width={w}
      style={{ width: w, height: "auto", display: "block" }}
      className={clsx("select-none flex-shrink-0", className)}
      draggable={false}
    />
  );
}
