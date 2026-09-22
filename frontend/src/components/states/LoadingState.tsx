import "./states.css";

export type LoadingStateProps = {
  message?: string;
};

export function LoadingState({
  message = "Loading...",
}: LoadingStateProps) {
  return (
    <div
      className="app-state app-state--loading"
      role="status"
      aria-live="polite"
    >
      <span
        className="app-state__spinner"
        aria-hidden="true"
      />

      <span>{message}</span>
    </div>
  );
}
