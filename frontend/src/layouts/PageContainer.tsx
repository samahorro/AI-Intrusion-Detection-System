import type {
  HTMLAttributes,
  PropsWithChildren,
} from "react";

import "./layout.css";

export type PageContainerProps =
  PropsWithChildren<
    HTMLAttributes<HTMLDivElement>
  >;

export function PageContainer({
  children,
  className = "",
  ...props
}: PageContainerProps) {
  const classes = [
    "app-page-container",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      {...props}
      className={classes}
    >
      {children}
    </div>
  );
}
