# IDS Event Data Contract

## Purpose

The RawEvent data contract defines the initial structure used to transfer
network event information from the Backend/Core System to the AI detection
component.

This is the initial Sprint 1 contract and may be updated during later
integration work.

## RawEvent Fields

| Field | Type | Required | Description |
|---|---|---|---|
| event_id | string | Yes | Unique identifier for the event |
| session_id | integer | Yes | Identifier for the related network session |
| timestamp | string | Yes | Event timestamp in ISO-8601 format |
| src_ip | string | Yes | Source IP address |
| dest_ip | string | Yes | Destination IP address |
| protocol | string | Yes | Network protocol such as TCP or UDP |
| src_port | integer/null | No | Source port when available |
| dest_port | integer/null | No | Destination port when available |
| payload_size | integer | Yes | Payload size in bytes |
| direction | string | Yes | inbound or outbound |

## Example RawEvent

```json
{
  "event_id": "evt-0001",
  "session_id": 10001,
  "timestamp": "2026-09-14T19:45:00Z",
  "src_ip": "192.168.1.15",
  "dest_ip": "192.168.1.20",
  "protocol": "TCP",
  "src_port": 51000,
  "dest_port": 443,
  "payload_size": 1200,
  "direction": "outbound"
}