import type {
  HTMLAttributes,
  PropsWithChildren,
} from "react";

import "./base.css";

export type CardProps = PropsWithChildren<
  HTMLAttributes<HTMLElement> & {
    title?: string;
    description?: string;
  }
>;

export function Card({
  title,
  description,
  children,
  className = "",
  ...props
}: CardProps) {
  const classes = ["base-card", className]
    .filter(Boolean)
    .join(" ");

  return (
    <section {...props} className={classes}>
      {title ? (
        <header className="base-card__header">
          <h2 className="base-card__title">{title}</h2>

          {description ? (
            <p className="base-card__description">
              {description}
            </p>
          ) : null}
        </header>
      ) : null}

      <div className="base-card__content">
        {children}
      </div>
    </section>
  );
}
