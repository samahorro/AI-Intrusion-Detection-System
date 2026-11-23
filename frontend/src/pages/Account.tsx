
import { Link } from "react-router-dom";

import { useAuth } from "../features/auth";
import "./Account.css";

// ============================================================
// Format Account Creation Date
// ============================================================

function formatAccountCreated(value?: string): string {
  if (!value) return "Not available";

  const parsed = new Date(value);

  if (Number.isNaN(parsed.getTime())) {
    return "Not available";
  }

  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

// ============================================================
// AEGIS Account Overview
// ============================================================

/**
 * Display read-only account information retrieved from
 * /auth/me through the shared authentication provider.
 */
export default function Account() {
  const { state } = useAuth();

  // Prevent stale account information from appearing
  // during authentication transitions.
  if (state.status !== "authenticated") {
    return null;
  }

  const { user } = state.session;

  return (
    <main
      className="account-page"
      aria-labelledby="account-heading"
    >
      <div className="account-page__inner">

        {/* ==================================================
            AEGIS Branding and Session Indicator
        ================================================== */}

        <div className="account-page__topline">
          <span className="account-page__brand">
            ◈ AEGIS <span>/ IDS</span>
          </span>

          <span className="account-page__session">
            <span
              className="account-page__session-dot"
              aria-hidden="true"
            />
            SECURE SESSION
          </span>
        </div>

        {/* ==================================================
            Account Page Heading
        ================================================== */}

        <header className="account-page__heading">
          <p className="account-page__eyebrow">
            AEGIS / USER PROFILE
          </p>

          <h1 id="account-heading">
            Account Overview
          </h1>

          <p>
            Your profile and active session details
            within AEGIS.
          </p>
        </header>

        {/* ==================================================
            Profile Information Card
        ================================================== */}

        <section
          className="account-page__card"
          aria-label="Profile information"
        >

          {/* Card Header */}

          <div className="account-page__card-topline">
            <span>
              PROFILE INFORMATION
            </span>

            <span className="account-page__read-only">
              READ ONLY
            </span>
          </div>

          {/* ==================================================
              User Identity
          ================================================== */}

          <div className="account-page__identity">
            <div
              className="account-page__avatar"
              aria-hidden="true"
            >
              {user.username.charAt(0).toUpperCase()}
            </div>

            <div className="account-page__identity-text">
              <h2>
                {user.username}
              </h2>

              <p>
                AEGIS User Account
              </p>
            </div>

            <span className="account-page__verified">
              ● SESSION ACTIVE
            </span>
          </div>

          {/* ==================================================
              Account Details
          ================================================== */}

          <dl className="account-page__details">

            {/* Username */}

            <div>
              <dt>
                USERNAME
              </dt>

              <dd>
                {user.username}
              </dd>
            </div>

            {/* User ID */}

            <div>
              <dt>
                USER ID
              </dt>

              <dd>
                {user.id}
              </dd>
            </div>

            {/* Account Creation Date */}

            <div>
              <dt>
                ACCOUNT CREATED
              </dt>

              <dd>
                {formatAccountCreated(user.createdAt)}
              </dd>
            </div>

          </dl>

          {/* ==================================================
              Read-Only Account Notice
          ================================================== */}

          <p className="account-page__note">
            <span aria-hidden="true">
              ⓘ
            </span>

            <span>
              Account details are managed by AEGIS and
              cannot be edited from this page.
            </span>
          </p>
        </section>

        {/* ==================================================
            Navigation and Footer
        ================================================== */}

        <div className="account-page__actions">
          <Link
            className="account-page__back"
            to="/console"
          >
            ← Back to Security Console
          </Link>

          <span className="account-page__footer-label">
            AEGIS / INTRUSION DETECTION
          </span>
        </div>

      </div>
    </main>
  );
}
