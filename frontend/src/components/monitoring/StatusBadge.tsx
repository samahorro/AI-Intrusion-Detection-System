interface StatusBadgeProps {
  status: "online" | "offline" | "scanning";
}

export default function StatusBadge({
  status,
}: StatusBadgeProps) {
  return (
    <span className={`status-badge ${status}`}>
      {status.toUpperCase()}
    </span>
  );
}