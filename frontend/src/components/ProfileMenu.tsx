
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../features/auth/useAuth";
import "./ProfileMenu.css";

type ProfileMenuProps = {
  username?: string;
};

export function ProfileMenu({
  username = "demo_user",
}: ProfileMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isSigningOut, setIsSigningOut] = useState(false);

  const menuRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const { logout } = useAuth();

  useEffect(() => {
    function handleOutsideClick(event: MouseEvent) {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
      document.removeEventListener(
        "keydown",
        handleEscape
      );
    };
  }, []);

  async function handleSignOut() {
    if (isSigningOut) return;

    setIsSigningOut(true);

    try {
      await logout();
      setIsOpen(false);
      navigate("/login", { replace: true });
    } catch (error) {
      console.error("Unable to sign out:", error);
      setIsSigningOut(false);
    }
  }

  return (
    <div className="aegis-profile" ref={menuRef}>
      <button
        type="button"
        className={`aegis-profile__trigger ${
          isOpen ? "aegis-profile__trigger--open" : ""
        }`}
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label="Account menu"
      >
        <div className="aegis-profile__avatar">
          <svg
            viewBox="0 0 64 64"
            aria-hidden="true"
            focusable="false"
          >
            <defs>
              <linearGradient
                id="aegis-avatar-gradient"
                x1="0%"
                y1="0%"
                x2="100%"
                y2="100%"
              >
                <stop offset="0%" stopColor="#db8bff" />
                <stop offset="55%" stopColor="#9276ec" />
                <stop offset="100%" stopColor="#1b5074" />
              </linearGradient>
            </defs>

            <circle
              cx="32"
              cy="32"
              r="31"
              fill="url(#aegis-avatar-gradient)"
            />
            <circle
              cx="32"
              cy="23"
              r="11"
              fill="rgba(255,255,255,0.94)"
            />
            <path
              d="M13 53c1-11 8-18 19-18s18 7 19 18"
              fill="rgba(255,255,255,0.94)"
            />
          </svg>
        </div>

        <span className="aegis-profile__username">
          {username}
        </span>

        <svg
          className={`aegis-profile__chevron ${
            isOpen ? "aegis-profile__chevron--open" : ""
          }`}
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          aria-hidden="true"
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>

      {isOpen && (
        <div className="aegis-profile__dropdown">
          <div className="aegis-profile__account">
            <div className="aegis-profile__avatar aegis-profile__avatar--large">
              <svg
                viewBox="0 0 64 64"
                aria-hidden="true"
                focusable="false"
              >
                <circle cx="32" cy="32" r="31" fill="#8051d4" />
                <circle cx="32" cy="23" r="11" fill="#ffffff" />
                <path
                  d="M13 53c1-11 8-18 19-18s18 7 19 18"
                  fill="#ffffff"
                />
              </svg>
            </div>

            <div>
              <strong>{username}</strong>
              <span>AEGIS Network Defense</span>
            </div>
          </div>

          <div className="aegis-profile__divider" />

          <button
            type="button"
            className="aegis-profile__logout"
            onClick={handleSignOut}
            disabled={isSigningOut}
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M10 17l5-5-5-5" />
              <path d="M15 12H3" />
              <path d="M12 3h6a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3h-6" />
            </svg>

            {isSigningOut ? "Signing out..." : "Sign out"}
          </button>
        </div>
      )}
    </div>
  );
}
