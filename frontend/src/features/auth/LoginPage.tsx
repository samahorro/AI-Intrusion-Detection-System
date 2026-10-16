
import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { Card } from "../../components/base";
import { AuthServiceError } from "../../services/auth/AuthServiceError";

import { GlobeActivityPopups } from "./GlobeActivityPopups";
import { LoginForm } from "./LoginForm";
import { useAuth } from "./useAuth";

import "./login.css";

// ==================================================
// AUTHENTICATION ERROR HANDLING
// Preserved from the current main branch
// ==================================================

function getLoginErrorMessage(error: unknown): string {
  if (error instanceof AuthServiceError) {
    switch (error.code) {
      case "INVALID_CREDENTIALS":
        return "The username or password is incorrect.";

      case "NETWORK_ERROR":
        return "Unable to reach the authentication service. Please try again.";

      case "SESSION_EXPIRED":
        return "Your session has expired. Please sign in again.";

      case "UNKNOWN_ERROR":
        return "Sign in failed. Please try again.";

      default:
        return "Sign in failed. Please try again.";
    }
  }

  return "Sign in failed. Please try again.";
}

// ==================================================
// ANIMATED GLOBE NETWORK CONNECTIONS
// Decorative simulation, not real network telemetry
// ==================================================

const networkRoutes = [
  "M 149 228 Q 263 60 415 163",
  "M 155 235 Q 272 110 375 306",
  "M 230 260 Q 338 178 457 250",
  "M 244 298 Q 315 185 351 386",
  "M 372 313 Q 476 154 526 277",
  "M 250 273 Q 220 349 309 454",
];

const networkEndpoints: [number, number][] = [
  [149, 228],
  [155, 235],
  [230, 260],
  [244, 298],
  [372, 313],
  [250, 273],
  [415, 163],
  [375, 306],
  [457, 250],
  [351, 386],
  [526, 277],
  [309, 454],
];

// ==================================================
// AEGIS ANIMATED BACKGROUND
// ==================================================

function AegisBackdrop() {
  return (
    <div className="aegis-backdrop" aria-hidden="true">
      <div className="aegis-backdrop__grid" />

      <div className="aegis-backdrop__light aegis-backdrop__light--left" />
      <div className="aegis-backdrop__light aegis-backdrop__light--right" />

      <div className="aegis-globe">
        <div className="aegis-globe__halo" />

        {/* Earth geography */}
        <img
          className="aegis-globe__sphere"
          src="/aegis-earth.svg"
          alt=""
          draggable={false}
        />

        {/* Animated network connections */}
        <svg
          className="aegis-globe__routes"
          viewBox="0 0 600 600"
          aria-hidden="true"
          focusable="false"
        >
          <defs>
            <linearGradient
              id="aegis-route-gradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop offset="0%" stopColor="#b987ff" />
              <stop offset="50%" stopColor="#ff91d8" />
              <stop offset="100%" stopColor="#8d7cff" />
            </linearGradient>

            <filter
              id="aegis-route-glow"
              x="-60%"
              y="-60%"
              width="220%"
              height="220%"
            >
              <feGaussianBlur stdDeviation="3.2" />
            </filter>

            <clipPath id="aegis-route-clip">
              <circle cx="300" cy="300" r="252" />
            </clipPath>
          </defs>

          {/* Routes */}
          <g
            className="aegis-globe__surface-routes"
            clipPath="url(#aegis-route-clip)"
          >
            {networkRoutes.map((path, index) => (
              <g key={path}>
                <path
                  d={path}
                  className="aegis-globe__route-glow"
                />

                <path
                  d={path}
                  className="aegis-globe__route-line"
                  style={{
                    animationDelay: `${index * -0.8}s`,
                  }}
                />
              </g>
            ))}
          </g>

          {/* Network endpoints */}
          <g className="aegis-globe__endpoints">
            {networkEndpoints.map(([cx, cy], index) => (
              <g
                key={`${cx}-${cy}`}
                className="aegis-globe__endpoint"
                style={{
                  animationDelay: `${index * -0.31}s`,
                }}
              >
                <circle
                  cx={cx}
                  cy={cy}
                  r="9"
                  fill="#d89bff"
                  opacity="0.14"
                />

                <circle
                  cx={cx}
                  cy={cy}
                  r="3.4"
                  fill="#f3d1ff"
                />
              </g>
            ))}
          </g>

          {/* Orbit rings */}
          <ellipse
            cx="300"
            cy="300"
            rx="288"
            ry="116"
            transform="rotate(-23 300 300)"
            className="aegis-globe__orbit"
          />

          <ellipse
            cx="300"
            cy="300"
            rx="278"
            ry="100"
            transform="rotate(36 300 300)"
            className="aegis-globe__orbit aegis-globe__orbit--second"
          />
        </svg>

        <div className="aegis-globe__ring aegis-globe__ring--one" />
        <div className="aegis-globe__ring aegis-globe__ring--two" />

        {/* Simulated network activity pop-ups */}
        <GlobeActivityPopups />
      </div>

      <div className="aegis-backdrop__scan" />
    </div>
  );
}

// ==================================================
// LOGIN PAGE
// Existing authentication functionality preserved
// ==================================================

export function LoginPage() {
  const navigate = useNavigate();
  const { state, login } = useAuth();

  const [errorMessage, setErrorMessage] = useState<string>();
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect authenticated users
  if (state.status === "authenticated") {
    return <Navigate to="/console" replace />;
  }

  const isCheckingSession =
    state.status === "loading" && !isSubmitting;

  return (
    <main className="auth-page">
      {/* Background */}
      <AegisBackdrop />

      {/* Branding */}
      <div
        className="auth-brand"
        aria-label="AEGIS Network Defense"
      >
        <span
          className="auth-brand__mark"
          aria-hidden="true"
        />

        <span className="auth-brand__text">
          AEGIS
        </span>

        <span className="auth-brand__subtitle">
          NETWORK DEFENSE
        </span>
      </div>

      {/* Login form */}
      <div className="auth-page__content">
        <div className="auth-page__eyebrow">
          SECURE ACCESS PORTAL
        </div>

        {isCheckingSession ? (
          <Card
            className="auth-card"
            title="Sign in"
            description="Checking your current session..."
          >
            <p
              className="auth-session-status"
              role="status"
            >
              Loading authentication state...
            </p>
          </Card>
        ) : (
          <Card
            className="auth-card"
            title="Welcome back"
            description="Sign in to your AEGIS account to continue."
          >
            <LoginForm
              isSubmitting={isSubmitting}
              errorMessage={errorMessage}
              onClearError={() => {
                setErrorMessage(undefined);
              }}
              onSubmit={async (credentials) => {
                setErrorMessage(undefined);
                setIsSubmitting(true);

                try {
                  await login(credentials);

                  navigate("/console", {
                    replace: true,
                  });
                } catch (error) {
                  setErrorMessage(
                    getLoginErrorMessage(error),
                  );
                } finally {
                  setIsSubmitting(false);
                }
              }}
            />
          </Card>
        )}

        {/* Slogan */}
        <p className="auth-page__slogan">
          ADAPTIVE SECURITY
          <span>•</span>
          CLEAR VISIBILITY
          <span>•</span>
          FASTER RESPONSE
        </p>
      </div>

      {/* Footer */}
      <div className="auth-page__footer">
        AEGIS <span>—</span> NETWORK INTRUSION DETECTION SYSTEM
      </div>
    </main>
  );
}
