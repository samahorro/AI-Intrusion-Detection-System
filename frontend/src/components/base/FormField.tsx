import type { PropsWithChildren } from "react";

import "./base.css";

export type FormFieldProps = PropsWithChildren<{
  id: string;
  label: string;
  hint?: string;
  error?: string;
  required?: boolean;
}>;

export function FormField({
  id,
  label,
  hint,
  error,
  required = false,
  children,
}: FormFieldProps) {
  return (
    <div className="base-form-field">
      <label className="base-form-field__label" htmlFor={id}>
        {label}
        {required ? (
          <span aria-hidden="true" className="base-form-field__required">
            {" "}*
          </span>
        ) : null}
      </label>

      {children}

      {hint && !error ? (
        <p
          id={`${id}-hint`}
          className="base-form-field__hint"
        >
          {hint}
        </p>
      ) : null}

      {error ? (
        <p
          id={`${id}-error`}
          className="base-form-field__error"
          role="alert"
        >
          {error}
        </p>
      ) : null}
    </div>
  );
}
