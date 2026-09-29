export interface DetectionFlow {
  "Flow Duration": number;
  "Total Fwd Packets": number;
  "Total Backward Packets": number;
  "Flow Bytes/s": number;
  "Flow Packets/s": number;
}

export interface DetectionEvent {
  failed_login_attempts?: number;
  ports_scanned?: number;
}

export interface DetectionRequest {
  flow: DetectionFlow;
  event?: DetectionEvent;
}

export interface DetectionInference {
  prediction: string | number | boolean;
  status: string;
}

export interface SignatureDetectionResult {
  detected: boolean;
  attack_type: string | null;
  severity: "normal" | "low" | "medium" | "high";
  reason: string;
}

export interface ThreatResult {
  detected: boolean;
  attack_type: string | null;
  threat_score: number;
  classification: "normal" | "low" | "medium" | "high";
}

export interface DetectionResponse {
  status: string;
  features: number[];
  inference: DetectionInference;
  signature: SignatureDetectionResult;
  threat: ThreatResult;
}