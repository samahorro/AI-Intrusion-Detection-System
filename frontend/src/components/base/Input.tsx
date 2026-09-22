import {
  forwardRef,
  type InputHTMLAttributes,
} from "react";

import "./base.css";

export type InputProps =
  InputHTMLAttributes<HTMLInputElement> & {
    hasError?: boolean;
  };

export const Input = forwardRef<HTMLInputElement, InputProps>(
  function Input(
    {
      hasError = false,
      className = "",
      ...props
    },
    ref,
  ) {
    const classes = [
      "base-input",
      hasError ? "base-input--error" : "",
      className,
    ]
      .filter(Boolean)
      .join(" ");

    return (
      <input
        {...props}
        ref={ref}
        className={classes}
        aria-invalid={hasError || undefined}
      />
    );
  },
);
