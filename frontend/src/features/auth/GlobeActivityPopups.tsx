
import "./GlobeActivityPopups.css";

type ActivityType = "success" | "warning" | "info";

type ActivityMessage = {
  id: number;
  title: string;
  lines: string[];
  type: ActivityType;
};

const activityMessages: ActivityMessage[] = [
  {
    id: 1,
    title: "ICMP RESPONSE",
    type: "success",
    lines: [
      "Pinging 192.168.1.1",
      "bytes=32 time=12ms TTL=64",
      "bytes=32 time=11ms TTL=64",
      "Packets received: 2",
    ],
  },
  {
    id: 2,
    title: "NETWORK CONNECTION",
    type: "info",
    lines: [
      "Source: 172.20.10.3",
      "Destination: 10.0.0.15",
      "Protocol: TCP",
      "Connection established",
    ],
  },
  {
    id: 3,
    title: "PACKET LOSS",
    type: "warning",
    lines: [
      "Request timed out.",
      "Packets: Sent = 3",
      "Received = 2",
      "Lost = 1 (33.3% loss)",
    ],
  },
  {
    id: 4,
    title: "PACKET CAPTURE",
    type: "success",
    lines: [
      "Source: 10.0.0.42",
      "Destination: 8.8.8.8",
      "Protocol: UDP",
      "Status: CAPTURED",
    ],
  },
  {
    id: 5,
    title: "TRAFFIC ANALYSIS",
    type: "info",
    lines: [
      "Network flow detected",
      "Packets processed: 128",
      "Protocol: TCP",
      "Status: ANALYZING",
    ],
  },
];

export function GlobeActivityPopups() {
  return (
    <div
      className="aegis-activity-layer"
      aria-hidden="true"
    >
      {activityMessages.map((message) => (
        <div
          key={message.id}
          className={[
            "aegis-activity-popup",
            `aegis-activity-popup--${message.id}`,
            `aegis-activity-popup--${message.type}`,
          ].join(" ")}
        >
          <div className="aegis-activity-popup__header">
            <span className="aegis-activity-popup__indicator" />

            <span className="aegis-activity-popup__title">
              {message.title}
            </span>

            <span className="aegis-activity-popup__status">
              DEMO
            </span>
          </div>

          <div className="aegis-activity-popup__body">
            {message.lines.map((line, index) => (
              <div
                className="aegis-activity-popup__line"
                key={`${message.id}-${index}`}
              >
                <span className="aegis-activity-popup__prompt">
                  {">"}
                </span>
                <span>{line}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
