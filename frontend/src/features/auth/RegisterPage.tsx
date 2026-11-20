import {
  useState,
} from "react";

import {
  Link,
  Navigate,
  useNavigate,
} from "react-router-dom";

import { Card } from "../../components/base";

import {
  registerUser,
} from "../../services/auth/registrationService";

import {
  RegisterForm,
} from "./RegisterForm";

import { useAuth } from "./useAuth";

import "./login.css";

export function RegisterPage() {
  const navigate = useNavigate();

  const { state } = useAuth();

  const [
    errorMessage,
    setErrorMessage,
  ] = useState<string>();

  const [
    isSubmitting,
    setIsSubmitting,
  ] = useState(false);

  if (
    state.status ===
    "authenticated"
  ) {
    return (
      <Navigate
        to="/console"
        replace
      />
    );
  }

  return (
    <main className="auth-page">
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

      <div className="auth-page__content">
        <div className="auth-page__eyebrow">
          ACCOUNT REGISTRATION
        </div>

        <Card
          className="auth-card"
          title="Create account"
          description="Create an AEGIS account to access the network defense console."
        >
          <RegisterForm
            isSubmitting={
              isSubmitting
            }
            errorMessage={
              errorMessage
            }
            onClearError={() => {
              setErrorMessage(
                undefined,
              );
            }}
            onSubmit={async (
              credentials,
            ) => {
              setErrorMessage(
                undefined,
              );

              setIsSubmitting(
                true,
              );

              try {
                await registerUser(
                  credentials,
                );

                navigate(
                  "/login",
                  {
                    replace: true,
                    state: {
                      registrationMessage:
                        "Account created successfully. Sign in to continue.",
                    },
                  },
                );
              } catch (error) {
                setErrorMessage(
                  error instanceof
                    Error
                    ? error.message
                    : "Unable to create account.",
                );
              } finally {
                setIsSubmitting(
                  false,
                );
              }
            }}
          />

          <p className="auth-account-link">
            Already have an account?{" "}
            <Link to="/login">
              Sign in
            </Link>
          </p>
        </Card>

        <p className="auth-page__slogan">
          ADAPTIVE SECURITY
          <span>•</span>
          CLEAR VISIBILITY
          <span>•</span>
          FASTER RESPONSE
        </p>
      </div>

      <div className="auth-page__footer">
        AEGIS <span>—</span>{" "}
        NETWORK INTRUSION
        DETECTION SYSTEM
      </div>
    </main>
  );
}