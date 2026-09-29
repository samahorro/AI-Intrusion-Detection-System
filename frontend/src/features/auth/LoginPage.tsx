import { useState } from "react";
import {
  Navigate,
  useNavigate,
} from "react-router-dom";

import { Card } from "../../components/base";
import { AuthServiceError } from "../../services/auth/AuthServiceError";

import { LoginForm } from "./LoginForm";
import { useAuth } from "./useAuth";

import "./login.css";

function getLoginErrorMessage(
  error: unknown,
): string {
  if (error instanceof AuthServiceError) {
    switch (error.code) {
      case "INVALID_CREDENTIALS":
        return "The email or password is incorrect.";

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

export function LoginPage() {
  const navigate = useNavigate();
  const { state, login } = useAuth();

  const [errorMessage, setErrorMessage] =
    useState<string>();

  const [isSubmitting, setIsSubmitting] =
    useState(false);

  if (state.status === "authenticated") {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }

  if (
    state.status === "loading" &&
    !isSubmitting
  ) {
    return (
      <main className="auth-page">
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
      </main>
    );
  }

  return (
    <main className="auth-page">
      <Card
        className="auth-card"
        title="Sign in"
        description="Use your AI-IDS account to continue."
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

              navigate(
                "/dashboard",
                { replace: true },
              );
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
    </main>
  );
}
