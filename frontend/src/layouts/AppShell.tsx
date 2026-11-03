import type {
  PropsWithChildren,
  ReactNode,
} from "react";
import { Link } from "react-router-dom";

import {
  getPrimaryNavigationRoutes,
  isRouteActive,
} from "../navigation";

import styles from "./AppShell.module.css";

export type AppShellProps = PropsWithChildren<{
  currentPath: string;
  userLabel?: string;
  headerActions?: ReactNode;
  contentTag?: "main" | "div";
}>;

export function AppShell({
  currentPath,
  userLabel,
  headerActions,
  contentTag = "main",
  children,
}: AppShellProps) {
  const navigation =
    getPrimaryNavigationRoutes();
  const Content = contentTag;

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <div className={styles.headerMain}>
          <Link
            className={styles.brand}
            to="/console"
          >
            AI-IDS
          </Link>

          <nav
            className={styles.navigation}
            aria-label="Primary navigation"
          >
            {navigation.map((route) => {
              const active = isRouteActive(
                currentPath,
                route.path,
              );

              return (
                <Link
                  key={route.id}
                  to={route.path}
                  className={
                    active
                      ? `${styles.navLink} ${styles.navLinkActive}`
                      : styles.navLink
                  }
                  aria-current={
                    active ? "page" : undefined
                  }
                  data-route-owner={route.owner}
                >
                  {route.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {(userLabel || headerActions) ? (
          <div className={styles.headerUtilities}>
            {userLabel ? (
              <span className={styles.userLabel}>
                {userLabel}
              </span>
            ) : null}

            {headerActions}
          </div>
        ) : null}
      </header>

      <Content className={styles.content}>
        {children}
      </Content>
    </div>
  );
}
