# NirmaanAI: Complete Reproducibility Checklist & Deployment Runbook
**System Version:** v0.25.0  
**Repository:** `C:\NIRMAAN AI`  
**Purpose:** Deterministic, step-by-step verification and reproduction manual for all NirmaanAI software components, data pipelines, model artifacts, and user interfaces.

---

## 1. System Requirements & Host Environment

### Hardware Prerequisites
- **Processor:** 64-bit multi-core x86_64 CPU (minimum 4 physical cores, 8 threads recommended).
- **RAM:** 8 GB minimum (16 GB recommended for concurrent backend, database, and Vite dev server).
- **Disk Storage:** 5 GB free space for repository, model artifacts, virtual environments, and node packages.
- **GPU:** Optional. All models (XGBoost, Random Forest, PCA, LightGBM, SVD) execute deterministically on CPU in sub-second intervals.

### Software Prerequisites
- **Operating System:** Windows 10/11, Linux (Ubuntu 22.04+ LTS), or macOS (Sonoma+).
- **Python:** Python `3.11.x` – `3.14.x` (Tested and verified on `Python 3.14.0`).
- **Node.js:** Node.js `18.x` or `20.x` LTS (Verified with `npm 10.x`).
- **Git:** Git `2.40+`.
- **Docker (Production Deployment):** Docker Engine `24.x+` with Docker Compose v2 (Note: host environment limitations documented in Section 9).

---

## 2. Repository Setup & Virtual Environment

### Step 2.1: Clone and Enter Root Directory
```bash
git clone https://github.com/Chirag04-bit/NirmaanAI.git
cd NirmaanAI
```

### Step 2.2: Setup Python Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 2.3: Install Python Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2.4: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 3. Dataset Verification & Integrity Auditing

### Step 3.1: Verify Operational Loss Dataset MD5 Checksum
To guarantee that the experimental financial ground truth has not been modified or corrupted:
```bash
# Windows PowerShell
Get-FileHash data/synthetic/auto_components/operational_losses.csv -Algorithm MD5

# Expected Output:
# Algorithm: MD5
# Hash: 34B12582B32D81E3121429C55EBF74E8
```

### Step 3.2: Verify Benchmark Datasets
Ensure all benchmark datasets exist in their respective directories:
- `data/ai4i2020/ai4i2020.csv`
- `data/cmapss/train_FD001.txt` & `test_FD001.txt`
- `data/uci_electricity/`
- `data/synthetic/`

---

## 4. Deterministic Model Artifacts & Training Reproduction

All models in NirmaanAI were trained with fixed random seeds (`random_state=42`) and deterministic solvers. Pre-trained weights and pipeline scalers are stored in `models/`:

| Subsystem | Saved Artifact Path | Associated Scaler / Pipeline | Decision Threshold |
| :--- | :--- | :--- | :--- |
| **Predictive Maintenance** | `models/pdm_xgboost.json` | `models/pdm_scaler.pkl` | $\tau = 0.9100$ |
| **RUL Prognostics** | `models/rul_rf.pkl` | `models/rul_scaler.pkl` | $RUL_{\text{max}} = 125$ |
| **Anomaly Detection** | `models/pca_anomaly.pkl` | `models/pca_scaler.pkl` | $\tau_{\text{recon}} = 0.24050$ |
| **Energy Forecasting** | `models/energy_lgbm.txt` | `models/energy_scaler.pkl` | Regression ($N=24$) |
| **Knowledge Retrieval (RAG)** | `models/knowledge/vector_index.npy` | `models/knowledge/dense_embedder.joblib` | Top-5 cosine ranking (256d) |

### Re-running Model Evaluation Scripts
To independently verify metric outputs without retraining:
```bash
# Evaluate PdM XGBoost on test split
python scripts/evaluate_pdm.py

# Evaluate PCA Anomaly Detector
python scripts/evaluate_anomaly.py

# Evaluate RAG Benchmark
python scripts/evaluate_rag.py
```

---

## 5. Database Setup & Seeding

### Step 5.1: Environment Configuration
Copy the template `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure key environment variables are defined:
```ini
ENVIRONMENT=production
DATABASE_URL=postgresql://nirmaan_user:nirmaan_secret_2026@localhost:5432/nirmaanai_db
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
DATASET_CHECKSUM=34B12582B32D81E3121429C55EBF74E8
TEMPORAL_CUTOFF=2026-01-21T12:00:00Z
```

### Step 5.2: Database Migration (PostgreSQL)
When running against a live PostgreSQL server:
```bash
# Run Alembic migrations to create 19 tables
alembic upgrade head
```

### Step 5.3: Execute Deterministic Data Seeder
Populate the database with the 5-station factory topology, baseline telemetry, and historical work orders:
```bash
python scripts/seed_database.py
```

---

## 6. Running the Local Application Stack

### Step 6.1: Launch FastAPI Backend Daemon
```bash
# From repository root
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- Health Check Endpoint: `http://127.0.0.1:8000/api/v1/health`

### Step 6.2: Launch React + Vite Dashboard
```bash
# In a new terminal
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
- Open browser at `http://127.0.0.1:5173/`

### Step 6.3: Production Frontend Build Verification
Verify that the React production bundle compiles without errors:
```bash
cd frontend
npm run build
```
Expected output:
```
dist/index.html                   0.82 kB │ gzip:  0.46 kB
dist/assets/index-*.css          18.42 kB │ gzip:  4.12 kB
dist/assets/index-*.js          242.15 kB │ gzip: 74.30 kB
✓ built in ~250ms
```

---

## 7. Automated Test Suite Execution

The test suite validates data schemas, ML models, API contracts, RAG retrieval, security guardrails, and stress concurrency.

### Step 7.1: Execute Full Test Suite
```bash
pytest tests/ -q
```

### Step 7.2: Expected Test Output
```
........................................................................ [ 20%]
........................................................................ [ 40%]
........................................................................ [ 60%]
........................................................................ [ 80%]
...................................................................ss    [100%]
================= 353 passed, 2 skipped, 9 warnings in 11.45s =================
```
*Note on Skipped Tests:* Exactly 2 tests are skipped (`test_live_postgresql_connection`, `test_live_docker_daemon`) due to documented host environment limitations.

---

## 8. Docker Deployment Packaging

NirmaanAI includes production-grade containerization specifications:
- `Dockerfile.backend`: Multi-stage Python 3.11-slim container with non-root security user (`nirmaan`).
- `frontend/Dockerfile`: Multi-stage Node build with Alpine Nginx serving static assets and proxying `/api/v1`.
- `docker-compose.prod.yml`: Coordinated orchestration of PostgreSQL 16, backend, and Nginx.

### Step 8.1: Build & Launch with Docker Compose
```bash
docker compose -f docker-compose.prod.yml up --build -d
```

### Step 8.2: Verify Container Health
```bash
docker compose -f docker-compose.prod.yml ps
```

---

## 9. Known Host Environment Limitations & Audit Notes

1. **Native PostgreSQL Daemon:** In the native Windows development environment, PostgreSQL 16 was not installed as a host system service. The system was validated using SQLite/In-Memory fallback layers while maintaining full Alembic migrations for Dockerized deployment.
2. **Docker Desktop Daemon:** Docker Engine was not installed on the native Windows development workstation. Packaging files were statically verified, but runtime containerization execution remains labeled as `HOLD — ENVIRONMENT BLOCKED`.
3. **Controlled Synthetic Telemetry:** Continuous sensor telemetry for the 5-station factory is generated deterministically and represents controlled benchmark behavior rather than real-time field hardware telemetry.
4. **Exploratory Bottleneck Threshold:** The bottleneck classification threshold ($\tau = 0.40$) was tuned post-hoc.
5. **Epistemic Retrospective Event:** Maintenance record `MAINT_0003` at `2026-01-22 16:30:00 UTC` is quarantined as ground truth and must never be provided as an input to prospective decision pipelines.

---
*End of Complete Reproducibility Checklist & Deployment Runbook.*
