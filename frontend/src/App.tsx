import type { PropsWithChildren } from "react";
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

import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import SecurityConsole from "./pages/SecurityConsole";
import "./App.css";

// Navigation only appears when the user is authenticated.
function AuthenticatedNavigation() {
  const { state, logout } = useAuth();
  const location = useLocation();

  // Preserve the Security Console's standalone layout.
  if (
    state.status !== "authenticated" ||
    location.pathname === "/console"
  ) {
    return null;
  }

  return (
    <nav className="nav-bar">
      <h2>AI-IDS</h2>

      <div className="nav-bar__links">
        <Link to="/dashboard">
          Dashboard
        </Link>

        <Link to="/alerts">
          Alerts
        </Link>

        <Link to="/console">
          Security Console
        </Link>

        <span className="nav-bar__user">
          {state.session.user.displayName}
        </span>

        <button
          type="button"
          className="nav-bar__logout"
          onClick={() => {
            void logout();
          }}
        >
          Sign out
        </button>
      </div>
    </nav>
  );
}

// Reusable protection for pages requiring authentication.
function ProtectedPage({
  children,
}: PropsWithChildren) {
  return (
    <ProtectedRoute>
      {children}
    </ProtectedRoute>
  );
}

// Application routing with authentication protection.
function ApplicationRoutes() {
  return (
    <div className="app-shell">
      <AuthenticatedNavigation />

      <Routes>
        <Route
          path="/"
          element={
            <ProtectedPage>
              <Navigate to="/console" replace />
            </ProtectedPage>
          }
        />

        <Route
          path="/login"
          element={<LoginPage />}
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedPage>
              <Dashboard />
            </ProtectedPage>
          }
        />

        <Route
          path="/alerts"
          element={
            <ProtectedPage>
              <Alerts />
            </ProtectedPage>
          }
        />

        <Route
          path="/console"
          element={
            <ProtectedPage>
              <SecurityConsole />
            </ProtectedPage>
          }
        />
      </Routes>
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