import type { PropsWithChildren } from "react";
import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import {
  AuthProvider,
  LoginPage,
  ProtectedRoute,
  useAuth,
} from "./features/auth";

import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";

import "./App.css";

function AuthenticatedNavigation() {
  const { state, logout } = useAuth();

  if (state.status !== "authenticated") {
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

function ProtectedPage({
  children,
}: PropsWithChildren) {
  return (
    <ProtectedRoute>
      {children}
    </ProtectedRoute>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="app-shell">
          <AuthenticatedNavigation />

          <Routes>
            <Route
              path="/"
              element={(
                <ProtectedPage>
                  <Navigate
                    to="/dashboard"
                    replace
                  />
                </ProtectedPage>
              )}
            />

            <Route
              path="/login"
              element={<LoginPage />}
            />

            <Route
              path="/dashboard"
              element={(
                <ProtectedPage>
                  <Dashboard />
                </ProtectedPage>
              )}
            />

            <Route
              path="/alerts"
              element={(
                <ProtectedPage>
                  <Alerts />
                </ProtectedPage>
              )}
            />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
