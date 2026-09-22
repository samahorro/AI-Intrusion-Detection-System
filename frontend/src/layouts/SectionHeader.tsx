import type { ReactNode } from "react";

import "./layout.css";

export type SectionHeaderProps = {
  title: string;
  description?: string;
  actions?: ReactNode;
};

export function SectionHeader({
  title,
  description,
  actions,
}: SectionHeaderProps) {
  return (
    <header className="app-section-header">
      <div>
        <h1 className="app-section-header__title">
          {title}
        </h1>

        {description ? (
          <p className="app-section-header__description">
            {description}
          </p>
        ) : null}
      </div>

      {actions ? (
        <div className="app-section-header__actions">
          {actions}
        </div>
      ) : null}
    </header>
  );
}
