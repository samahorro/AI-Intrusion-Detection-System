import {
  BrowserRouter,
  Link,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import { AuthProvider, LoginPage } from "./features/auth";
import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import SecurityConsole from "./pages/SecurityConsole";
import "./App.css";

function ApplicationRoutes() {
  const location = useLocation();
  const isConsole = location.pathname === "/console";
  return (
    <div className="app-shell">
      {!isConsole && (
        <nav className="nav-bar">
          <h2>AI-IDS</h2>
          <div>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/alerts">Alerts</Link>
            <Link to="/console">Security Console</Link>
          </div>
        </nav>
      )}
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/console" element={<SecurityConsole />} />
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
