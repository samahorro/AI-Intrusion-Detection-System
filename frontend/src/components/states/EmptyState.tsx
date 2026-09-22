import type { ReactNode } from "react";

import "./states.css";

export type EmptyStateProps = {
  title: string;
  message?: string;
  action?: ReactNode;
};

export function EmptyState({
  title,
  message,
  action,
}: EmptyStateProps) {
  return (
    <section className="app-state app-state--empty">
      <h2>{title}</h2>

      {message ? <p>{message}</p> : null}

      {action ? (
        <div className="app-state__action">
          {action}
        </div>
      ) : null}
    </section>
  );
}
