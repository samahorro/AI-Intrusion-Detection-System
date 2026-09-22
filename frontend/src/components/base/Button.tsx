import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

import "./base.css";

export type ButtonVariant =
  | "primary"
  | "secondary"
  | "danger"
  | "ghost";

export type ButtonProps = PropsWithChildren<
  ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: ButtonVariant;
    isLoading?: boolean;
    loadingLabel?: string;
  }
>;

export function Button({
  variant = "primary",
  isLoading = false,
  loadingLabel = "Working...",
  disabled,
  className = "",
  children,
  type = "button",
  ...props
}: ButtonProps) {
  const classes = [
    "base-button",
    `base-button--${variant}`,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button
      {...props}
      type={type}
      className={classes}
      disabled={disabled || isLoading}
      aria-busy={isLoading || undefined}
    >
      {isLoading ? loadingLabel : children}
    </button>
  );
}
