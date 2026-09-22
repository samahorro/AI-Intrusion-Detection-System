import type { ReactNode } from "react";

import "./states.css";

export type ErrorStateProps = {
  title?: string;
  message: string;
  action?: ReactNode;
};

export function ErrorState({
  title = "Something went wrong",
  message,
  action,
}: ErrorStateProps) {
  return (
    <section
      className="app-state app-state--error"
      role="alert"
    >
      <h2>{title}</h2>
      <p>{message}</p>

      {action ? (
        <div className="app-state__action">
          {action}
        </div>
      ) : null}
    </section>
  );
}
