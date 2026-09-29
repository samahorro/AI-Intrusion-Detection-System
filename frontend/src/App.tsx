import {
  BrowserRouter,
  Link,
  Route,
  Routes,
} from "react-router-dom";

import {
  AuthProvider,
  LoginPage,
} from "./features/auth";

import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";

import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="app-shell">
          <nav className="nav-bar">
            <h2>AI-IDS</h2>

            <div>
              <Link to="/dashboard">
                Dashboard
              </Link>

              <Link to="/alerts">
                Alerts
              </Link>
            </div>
          </nav>

          <Routes>
            <Route
              path="/"
              element={<Dashboard />}
            />

            <Route
              path="/login"
              element={<LoginPage />}
            />

            <Route
              path="/dashboard"
              element={<Dashboard />}
            />

            <Route
              path="/alerts"
              element={<Alerts />}
            />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
