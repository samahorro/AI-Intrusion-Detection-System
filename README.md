# AEGIS — AI Intrusion Detection System

**CPSC 491 | Capstone Project | Local development**

AEGIS is a network monitoring and experimental intrusion detection platform combining live packet capture, flow-based analytics, signature-based rules, and a machine-learning model trained on the CICIDS2017 dataset. A React Security Console provides access to capture controls, live metrics, and detection results.

> **Development status:** AEGIS is a capstone prototype, not a production-ready IDS. The Random Forest inference path is experimental: equivalence between live-capture features and the CICIDS2017 training features has not yet been established. Do not treat predictions as independently verified security alerts.

## Screenshots

> Add the screenshots to `docs/screenshots/` using the filenames below. GitHub will display them directly in this README. Capture the application after starting the backend and frontend, and avoid exposing real IP addresses, account details, or sensitive alerts in public screenshots.

### Security Console

![AEGIS Security Console showing live packet capture and network telemetry](docs/screenshots/security-console.png)

*AEGIS dashboard with capture controls, traffic statistics, and experimental detection status.*

### Sign-in experience

![AEGIS sign-in page with animated globe](docs/screenshots/login.png)

*AEGIS authentication interface with the animated globe design.*

### Account registration (local development)

![AEGIS create account page](docs/screenshots/signup.png)

*Local signup experience. Registration policies should be reviewed before public deployment.*

### AI detection panel

![AEGIS experimental Random Forest predictions](docs/screenshots/ai-detection.png)

*Experimental prediction interface. Include this screenshot only after model loading and inference have been verified.*

## Key Features

- **Live network capture:** TShark-based packet capture with available-interface discovery and start/stop controls.
- **Network telemetry:** Packet and traffic statistics displayed in the Security Console.
- **Flow aggregation:** Experimental processing of observed traffic into bidirectional network-flow information and feature vectors.
- **Machine learning:** Binary Random Forest intrusion classifier developed with CICIDS2017 data, supported by local training notebooks, saved model artifacts, and evaluation reports.
- **Signature detection:** Existing rule-based checks for events such as repeated failed logins or port scanning, plus reusable signature rule definitions.
- **Authentication:** User login, session management, registration endpoint, and login-attempt/lockout protection.
- **Web UI:** React/TypeScript frontend with a Security Console, dashboard, and authentication screens.
- **Testing:** Backend, ML, and frontend tests and build tooling.

## Technology Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React, TypeScript, Vite, React Router |
| Backend | Python, FastAPI, SQLAlchemy |
| Network monitoring | TShark / Wireshark, flow aggregation |
| Machine learning | scikit-learn Random Forest, joblib, CICIDS2017 |
| Data science | Python, Jupyter notebooks, evaluation reports |
| Development database | SQLite by default; configurable with `DATABASE_URL` |
| Testing | pytest; Vitest / frontend build |

## System Architecture

```text
Network traffic
    |
    v
TShark packet capture
    |
    v
Capture service / flow aggregation
    |
    +----------------------+
    |                      |
    v                      v
Signature detection    Experimental ML inference
                           |
                           v
                     CICIDS2017 Random Forest
    |                      |
    +-----------+----------+
                |
                v
         FastAPI endpoints
                |
                v
    React AEGIS Security Console
```

The signature and ML paths are at different stages of integration. An Nmap scan being visible in packet capture does **not** by itself prove that AEGIS identified a port scan or generated a reliable alert.

## Local Setup — Windows PowerShell

### Prerequisites

- Python and Node.js/npm
- Wireshark with **TShark** and **Npcap** for live packet capture
- Git
- A local clone of this repository

### 1. Install Python dependencies

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Use the Python environment configured for the project. If the required tools are already installed, you can reuse the existing `.venv`.

### 2. Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

### 3. Configure the experimental model (optional)

Model inference requires a trained local `.joblib` model and its matching `.metadata.json` file. These files may be omitted from the Git repository and must be generated or obtained separately.

For the existing local CICIDS2017 baseline artifact:

```powershell
$env:MODEL_PATH = (Resolve-Path ".\ml\models\cicids2017_baseline\aegis_cicids2017_binary_rf_v1.joblib").Path
```

Run this command **in the same terminal** that starts FastAPI. The model and metadata must match. If you do not have these files, the experimental prediction endpoint may return `503 Service Unavailable`.

### 4. Start the backend

From the repository root:

```powershell
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

API documentation: `http://127.0.0.1:8000/docs`

### 5. Start the frontend

In a second terminal:

```powershell
cd frontend
npm run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173/`).

### 6. Start packet capture

Sign in to AEGIS, select the appropriate interface in the Security Console, and use the capture controls. Capture requires an appropriate TShark installation and operating-system permissions. Use only on networks and devices you own or are authorized to monitor.

## Experimental AI Model

The CICIDS2017 development artifacts are organized locally under:

```text
ml/
  notebooks/                         # Exploration, cleaning, feature engineering, training
  models/cicids2017_baseline/        # Random Forest artifact and model metadata
  evaluation/cicids2017_baseline/    # Metrics, reports and figures
```

Representative notebooks include:

- `09_CICIDS2017_Combined_Dataset_Preparation.ipynb`
- `10_CICIDS2017_Feature_Engineering_and_Training_Preparation.ipynb`
- `11_CICIDS2017_Binary_IDS_Model_Training_and_Evaluation.ipynb`

When the model is configured and the backend route is available, the experimental endpoint is:

```text
GET /capture/experimental-predictions
```

This endpoint uses completed flows and attempts classification using the trained model. It is authentication-protected. It is **not** a confirmed production alerting pipeline; further work is required to validate live feature parity, detection accuracy, and operational behavior.

## Authentication and Registration

The FastAPI backend exposes authentication endpoints including registration and login. The development frontend includes sign-in and locally implemented sign-up screens. In local development, the sign-up form collects a username and password (with client-side password confirmation). First- and last-name persistence has **not** been implemented yet.

**Security:** Review self-registration, access-control policy, session secrets, HTTPS settings, and deployment configuration before exposing AEGIS outside a trusted local development environment.

## Testing and Validation

From the repository root:

```powershell
python -m pytest backend/tests ml/tests -q
```

For the frontend:

```powershell
cd frontend
npm run test
npm run build
```

**Latest local test observation:** 254 passed and 1 failed in the backend/ML suite. The failing test, `test_missing_model_configuration`, expected HTTP 503 but received HTTP 200; an environment with `MODEL_PATH` set is a possible cause and needs verification. The suite has previously passed 255 tests in an unmodified configuration. Do not describe the current suite as fully passing until this is resolved.

## Current Limitations and Roadmap

- Validate that live TShark flow features use the same definitions and ordering as the CICIDS2017 training features.
- Confirm the trained model loads with its matching metadata and performs inference on completed live flows.
- Connect signature rules to observed network activity, including distinct destination-port counting for port-scan detection.
- Distinguish packet-capture success, model prediction, and verified intrusion alerts.
- Expand tests for model configuration, authentication, capture integration, and frontend state handling.
- Review sign-up authorization before public deployment.

## Project Documentation

- [CI/CD Workflow and Local Validation Guide](docs/ci-cd-workflow.md)
- [Frontend development guide](frontend/README.md)

## Screenshot Setup

Create a folder for README images in the repository:

```powershell
New-Item -ItemType Directory -Force -Path .\docs\screenshots
```

Save your captures as:

```text
docs/screenshots/security-console.png
docs/screenshots/login.png
docs/screenshots/signup.png
docs/screenshots/ai-detection.png
```

Use the same filenames as the Markdown references above. Do not upload images containing credentials, tokens, identifiable traffic, or sensitive host details. A screenshot only needs to be committed when you choose to publish it.

---

**AEGIS is under active development as a capstone project.**
