import type { PropsWithChildren } from "react";
import {
  Navigate,
  useLocation,
} from "react-router-dom";

import { ErrorState, LoadingState } from "../../components/states";

import { useAuth } from "./useAuth";

export function ProtectedRoute({
  children,
}: PropsWithChildren) {
  const { state, refreshSession } = useAuth();
  const location = useLocation();

  if (state.status === "loading") {
    return (
      <LoadingState
        message="Checking your AI-IDS session..."
      />
    );
  }

  if (state.status === "unavailable") {
    return (
      <main className="page">
        <ErrorState
          title="Unable to verify your session"
          message="The authentication service is unreachable. Your session has not been marked expired. Try again when the connection is restored."
          action={(
            <button type="button" onClick={() => { void refreshSession(); }}>
              Retry session check
            </button>
          )}
        />
      </main>
    );
  }

  if (state.status === "anonymous") {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location.pathname, reason: state.reason }}
      />
    );
  }

  return children;
}
