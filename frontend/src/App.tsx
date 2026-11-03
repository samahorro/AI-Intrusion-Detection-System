import type { PropsWithChildren, ReactNode } from "react";
import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";

import {
  AuthProvider,
  LoginPage,
  ProtectedRoute,
  useAuth,
} from "./features/auth";
import { AppShell } from "./layouts";
import { appRouteRegistry } from "./navigation";
import Account from "./pages/Account";
import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import SecurityConsole from "./pages/SecurityConsole";
import "./App.css";

/** Keep the registry as the source of truth for routable paths and navigation. */
const pageByRouteId: Readonly<Record<string, ReactNode>> = {
  login: <LoginPage />,
  dashboard: <Dashboard />,
  alerts: <Alerts />,
  console: <SecurityConsole />,
  account: <Account />,
};

function ProtectedPage({ children }: PropsWithChildren) {
  return <ProtectedRoute>{children}</ProtectedRoute>;
}

function AuthenticatedLayout({ children }: PropsWithChildren) {
  const { state, logout } = useAuth();
  const { pathname } = useLocation();

  // Keep Kevin's Security Console and the login portal standalone.
  if (
    state.status !== "authenticated" ||
    pathname === "/console" ||
    pathname === "/login"
  ) {
    return <>{children}</>;
  }

  return (
    <AppShell
      contentTag="div"
      currentPath={pathname}
      userLabel={state.session.user.displayName}
      headerActions={(
        <button
          type="button"
          className="nav-bar__logout"
          onClick={() => { void logout(); }}
        >
          Sign out
        </button>
      )}
    >
      {children}
    </AppShell>
  );
}

function NotFound() {
  return (
    <main className="page">
      <h1>Page not found</h1>
      <p>This AEGIS page does not exist or is not available yet.</p>
      <Link to="/console">Return to Security Console</Link>
    </main>
  );
}

function ApplicationRoutes() {
  return (
    <div className="app-shell">
      <AuthenticatedLayout>
        <Routes>
          <Route
            path="/"
            element={(
              <ProtectedPage>
                <Navigate to="/console" replace />
              </ProtectedPage>
            )}
          />

          {appRouteRegistry.map((route) => {
            const page = pageByRouteId[route.id];
            // The planned /admin/users route has no view yet, so do not
            // expose a broken route or advertise it as implemented.
            if (page === undefined) return null;

            return (
              <Route
                key={route.id}
                path={route.path}
                element={route.requiresAuth
                  ? <ProtectedPage>{page}</ProtectedPage>
                  : page}
              />
            );
          })}

          <Route
            path="*"
            element={<ProtectedPage><NotFound /></ProtectedPage>}
          />
        </Routes>
      </AuthenticatedLayout>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ApplicationRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
