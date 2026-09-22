import type {
  PropsWithChildren,
  ReactNode,
} from "react";

import {
  getPrimaryNavigationRoutes,
  isRouteActive,
} from "../navigation";

import styles from "./AppShell.module.css";

export type AppShellProps = PropsWithChildren<{
  currentPath: string;
  userLabel?: string;
  headerActions?: ReactNode;
}>;

export function AppShell({
  currentPath,
  userLabel,
  headerActions,
  children,
}: AppShellProps) {
  const navigation =
    getPrimaryNavigationRoutes();

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <div className={styles.headerMain}>
          <a
            className={styles.brand}
            href="/dashboard"
          >
            AI-IDS
          </a>

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
                <a
                  key={route.id}
                  href={route.path}
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
                </a>
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

      <main className={styles.content}>
        {children}
      </main>
    </div>
  );
}
