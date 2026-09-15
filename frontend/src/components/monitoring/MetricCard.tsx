interface MetricCardProps {
  title: string;
  value: number | string;
}

export default function MetricCard({
  title,
  value,
}: MetricCardProps) {
  return (
    <div className="metric-card">
      <h3>{title}</h3>
      <p>{value}</p>
    </div>
  );
}