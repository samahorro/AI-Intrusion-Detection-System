# Sprint 5 — Threat Scoring and Classification Validation

**Project:** AEGIS — AI-Powered Intrusion Detection System  
**Course:** CPSC 491  
**Sprint:** 5 — Threat Scoring and Classification  
**Development branch:** `SPRINT-threat-scoring-feature`  
**Validation status:** Automated backend and ML tests passed; deployment and live-traffic performance not established.

## 1. Purpose and Scope

Sprint 5 implemented and tested a reusable threat-scoring workflow combining machine-learning (ML) inference with signature-based intrusion detection. This document describes the scoring policy, severity classification, API integration, validation evidence, and current limitations.

The scope includes:

- Classifying normalized scores on a 0–100 scale.
- Using the ML model's estimated attack probability when available.
- Mapping signature severities to predefined scoring values.
- Combining active ML and signature evidence using the larger scoring confidence.
- Validating confidence inputs and handling unsupported model outputs.
- Verifying the implementation with automated unit and end-to-end tests.

## 2. Scoring and Classification Policy

The reusable scoring module is `ml/scoring/threat_scoring.py`. Its main functions are:

| Function | Responsibility |
| --- | --- |
| `validate_confidence()` | Accept finite numeric confidence values in the inclusive range 0.0–1.0; reject booleans, non-finite values, and out-of-range values. |
| `classify_score()` | Map an integer score between 0 and 100 to a classification. |
| `combine_detection_confidence()` | Select the strongest confidence contributed by an active detection source. |
| `score_threat()` | Return detection status, attack type, numerical threat score, and classification. |

### 2.1 Classification thresholds

| Threat score | Classification | Meaning in this scoring policy |
| --- | --- | --- |
| 0 | `normal` | Neither detection source reported an attack. |
| 1–39 | `low` | Low assigned threat score. |
| 40–69 | `medium` | Medium assigned threat score. |
| 70–100 | `high` | High assigned threat score. |

When `detected=False`, the score is 0. When `detected=True`, the score is calculated as `max(1, round(confidence * 100))`. Therefore, a detected event has a minimum score of 1. The returned classification is calculated from that integer score.

### 2.2 Machine-learning evidence

`ml/models/inference.py` provides model predictions and, for supported classifiers, an `attack_probability`. The detection route uses that probability to calculate the ML scoring contribution when the prediction indicates an attack. For prediction-only models that do not provide a probability, the current implementation falls back to 1.0, producing a score of 100 for a detected attack.

**Interpretation:** An estimated model probability is used as a scoring input; it has not been demonstrated here to be calibrated to real-world attack risk. The 1.0 fallback indicates unavailable probability information, not independently measured certainty.

### 2.3 Signature-based evidence

`ml/detection/signature_detection.py` identifies supported rule-based patterns, including brute-force and port-scan indicators. The backend route maps returned severities as follows:

| Signature severity | Confidence mapping | Score for a detected event |
| --- | ---: | ---: |
| `normal` | 0.0 | 0 when not detected |
| `low` | 0.3 | 30 |
| `medium` | 0.6 | 60 |
| `high` | 0.9 | 90 |

These values are **predefined heuristic mappings**, not probabilities measured or learned from data. In current tested scenarios, `failed_login_attempts >= 5` triggers a high-severity brute-force signature, and `ports_scanned >= 20` triggers a medium-severity port-scan signature.

### 2.4 Combined detection policy

For each detection source, inactive evidence contributes 0. The combined confidence is:

```python
combined_confidence = max(
    ml_confidence if ml_detected else 0.0,
    signature_confidence if signature_detected else 0.0,
)
```

This is a **maximum-evidence policy**: it does not sum the confidence values or assume that ML and signature detections are statistically independent. When a known signature is detected, its specific attack type is retained in the API result, even if the ML evidence determines the higher score. Otherwise, an ML-only detection uses `ml_detected` as the attack type.

## 3. API Integration and Input Validation

The authenticated FastAPI endpoint `POST /detection/analyze`, implemented in `backend/app/detection/routes.py`, performs these operations:

1. Preprocess the submitted network-flow features.
2. Run ML inference.
3. Evaluate signature detection against the event fields.
4. Normalize the model prediction into an attack or benign outcome.
5. Combine active evidence using `combine_detection_confidence()`.
6. Compute the final score and classification using `score_threat()`.
7. Return the `status`, `features`, `inference`, `signature`, and `threat` fields.

The threat result preserves the fields `detected`, `attack_type`, `threat_score`, and `classification`.

Input validation covers invalid confidence values (`NaN`, infinity, booleans, and values outside 0.0–1.0), invalid scores, and unsupported model prediction labels. In the tested API scenarios, unsupported predictions and invalid attack probabilities produce an HTTP 400 response. This is controlled application-level rejection rather than a successful detection result.

## 4. Verified Detection Scenarios

The following results correspond to the automated tests that were reported as passing during Sprint 5:

| Scenario | Expected result | Classification / API outcome | Relevant test |
| --- | --- | --- | --- |
| Benign network flow, no signature | Score 0 | `normal` | `test_detection_e2e_benign_flow` |
| ML attack, probability 0.85 | Score 85 | `high` | `test_detection_e2e_ml_probability_scoring` |
| Brute-force signature, benign ML prediction | Score 90 | `high` | `test_detection_e2e_signature_attack` |
| Port-scan signature, benign ML prediction | Score 60 | `medium` | `test_detection_e2e_port_scan_signature` |
| ML confidence 0.85 and port-scan severity 0.60 | Score 85 | `high` | `test_combined_detection_uses_higher_ml_score` |
| ML confidence 0.75 and brute-force severity 0.90 | Score 90 | `high` | `test_combined_detection_uses_higher_signature_score` |
| Unsupported ML prediction label `unknown` | HTTP 400 | Rejected | `test_detection_e2e_invalid_prediction_returns_400` |
| Invalid ML attack probability 1.2 | HTTP 400 | Rejected | `test_detection_e2e_invalid_probability_returns_400` |

The probability-based and combined-detection tests use lightweight test models. These results validate code behavior for defined cases, not production model accuracy on live traffic.

## 5. Automated Test Evidence

### 5.1 Focused tests

| Test file | Passed cases |
| --- | ---: |
| `ml/tests/test_threat_scoring_classification.py` | 40 |
| `ml/tests/test_preprocessing_inference.py` | 12 |
| `backend/tests/test_detection_route_helpers.py` | 25 |
| `backend/tests/test_detection_e2e.py` | 9 |
| **Total focused coverage** | **86** |

The 40 scoring tests cover classification boundaries, input validation, confidence combination, and inactive evidence. The 25 route-helper tests include four parameterized unknown-prediction cases. The nine end-to-end tests include both invalid-prediction and invalid-probability HTTP 400 cases.

### 5.2 Verified test commands and results

**End-to-end detection tests:**

```powershell
python -m pytest backend/tests/test_detection_e2e.py -v
```

Result: **9 passed, 1 warning**.

**Detection route helper and end-to-end tests:**

```powershell
python -m pytest backend/tests/test_detection_route_helpers.py backend/tests/test_detection_e2e.py -v
```

Result: **34 passed, 1 warning**.

**Complete backend and ML regression suite:**

```powershell
python -m pytest backend/tests ml/tests -q
```

Result: **539 passed, 1 warning in 107.62 seconds**.

The reported warning is `StarletteDeprecationWarning` from the installed FastAPI/Starlette test-client dependency, concerning use of `httpx`. No tests failed in the final reported run. The warning should be tracked as a dependency-maintenance item rather than treated as a functional test failure.

## 6. Files Implemented or Updated During Sprint 5

| File | Role |
| --- | --- |
| `ml/scoring/threat_scoring.py` | Reusable validation, classification, confidence-combination, and threat-scoring functions. |
| `ml/models/inference.py` | Exposes attack probability when supported by the model. |
| `backend/app/detection/routes.py` | Coordinates inference, signatures, confidence combination, scoring, and HTTP error handling. |
| `ml/tests/test_threat_scoring_classification.py` | Scoring boundaries, validation, and evidence-combination tests. |
| `ml/tests/test_preprocessing_inference.py` | Preprocessing, inference, probability, and backward-compatibility tests. |
| `backend/tests/test_detection_route_helpers.py` | Prediction normalization and signature severity tests. |
| `backend/tests/test_detection_e2e.py` | API-level detection, combination, and HTTP 400 regression tests. |

## 7. Known Limitations and Follow-Up Work

1. **Heuristic severity mapping:** Signature severities are mapped to fixed values of 0.0, 0.3, 0.6, and 0.9. They are not empirically calibrated attack probabilities.
2. **Uncalibrated risk interpretation:** ML `attack_probability` is used as scoring evidence, but this documentation does not establish probability calibration or real-world risk accuracy.
3. **Prediction-only model fallback:** When a model reports an attack but cannot provide a probability, the existing fallback is 1.0. This yields a high score without corresponding confidence measurement.
4. **Maximum-evidence rule:** The combined score preserves the stronger signal but does not represent a probabilistic fusion model or capture interactions between independent sources.
5. **Partial signature coverage:** The tested signature logic covers specific brute-force and port-scan indicators, not a comprehensive intrusion-signature library.
6. **Live-traffic validity not established:** Passing unit and API tests does not demonstrate that incoming live network-flow features exactly match CIC-IDS2017 training features, or that detection performance meets a production acceptance threshold.
7. **Dependency warning:** A FastAPI/Starlette test-client deprecation warning remains in the test output and may need attention during dependency maintenance.

## 8. Sprint 5 Validation Conclusion

Sprint 5 implemented reusable threat scoring, severity classification, ML probability-based scoring, signature severity integration, maximum-evidence combination, and controlled validation of unsupported model outputs. The final reported automated regression run completed with **539 passed, 0 failed, and 1 third-party deprecation warning**.

These results support completion of the sprint's **implementation and automated validation scope**. They do not by themselves verify live detection accuracy, production readiness, peer review, pull-request merge, or CI/CD success. Those activities require separate evidence from deployment testing and the repository's review and CI workflow.
