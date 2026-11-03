import { Link } from "react-router-dom";

import { useAuth } from "../features/auth";
import "./Account.css";

function formatMemberSince(value?: string): string {
  if (!value) return "Not available";

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Not available";

  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

/** Read-only account details sourced from /auth/me via the shared AuthProvider. */
export default function Account() {
  const { state } = useAuth();

  // The /account route is wrapped in ProtectedRoute; this guard prevents
  // any stale or anonymous account data from appearing during transitions.
  if (state.status !== "authenticated") return null;

  const { user } = state.session;

  return (
    <main className="account-page" aria-labelledby="account-heading">
      <header className="account-page__heading">
        <p className="account-page__eyebrow">AEGIS / ACCOUNT</p>
        <h1 id="account-heading">Your account</h1>
        <p>View the identity associated with your active AEGIS session.</p>
      </header>

      <div className="account-page__card">
        <div className="account-page__identity">
          <div className="account-page__avatar" aria-hidden="true">
            {user.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2>{user.username}</h2>
            <p>Authenticated AEGIS account</p>
          </div>
        </div>

        <dl className="account-page__details">
          <div>
            <dt>Username</dt>
            <dd>{user.username}</dd>
          </div>
          <div>
            <dt>Account ID</dt>
            <dd>{user.id}</dd>
          </div>
          <div>
            <dt>Member since</dt>
            <dd>{formatMemberSince(user.createdAt)}</dd>
          </div>
        </dl>

        <p className="account-page__note">
          Profile information is read-only. Editing account details requires a
          supported backend endpoint and separate authorization review.
        </p>
      </div>

      <Link className="account-page__back" to="/console">
        Return to Security Console
      </Link>
    </main>
  );
}
