# PERT and Critical Path Analysis for Smart Transportation Applications

**Academic Year:** 2026-27 | **Course:** DevSecOps Lab (CIAP Microproject)  
**Student:** Om Vivek Mehta | **Roll Number:** TYCS_25 | **PRN:** 124BTCS1021  
**Institution:** Shah and Anchor Kutchhi Engineering College (SAKEC), Department of Cybersecurity  
**SDG Alignment:** Primary: **SDG 9** (Industry, Innovation and Infrastructure) | Supporting: **SDG 11** (Sustainable Cities and Communities)

---

## 1. Project Overview

Municipal smart transportation projects (such as GPS fleet telemetry, automated passenger counting, and live transit routing) require deterministic dependency management across hardware procurement, backend cloud ingestion, and client mobile development.

This web application provides quantitative schedule management under uncertainty using:
- **PERT (Program Evaluation and Review Technique):** Models 3-point time estimates (Optimistic, Most Likely, Pessimistic) using Beta distribution approximations.
- **CPM (Critical Path Method):** Determines Early Start, Early Finish, Late Start, Late Finish, and Activity Slack via topological passes across a Directed Acyclic Graph (DAG).
- **Probabilistic Risk Modeling:** Computes project standard deviation and Normal Distribution completion probability using Z-score statistics.
- **Visual Analytics:** Real-time SVG network diagram highlighting the critical path(s) and a dynamic Gantt schedule.

---

## 2. Mathematical Modeling and Formulations

For every activity $i$:
1. **Expected Time ($T_E$):**
   $$T_E = \frac{O + 4M + P}{6}$$
2. **Variance ($\sigma^2$):**
   $$\sigma^2 = \left(\frac{P - O}{6}\right)^2$$
3. **Standard Deviation ($\sigma$):**
   $$\sigma = \frac{P - O}{6}$$
4. **Forward Pass (Early Start & Early Finish):**
   $$ES_i = \max_{p \in \text{Pred}(i)} (EF_p), \quad ES_{\text{start}} = 0$$
   $$EF_i = ES_i + T_{E,i}$$
5. **Project Duration ($T_{\text{project}}$):**
   $$T_{\text{project}} = \max_{i} (EF_i)$$
6. **Backward Pass (Late Finish & Late Start):**
   $$LF_i = \min_{s \in \text{Succ}(i)} (LS_s), \quad LF_{\text{end}} = T_{\text{project}}$$
   $$LS_i = LF_i - T_{E,i}$$
7. **Total Slack (Float):**
   $$\text{Slack}_i = LS_i - ES_i = LF_i - EF_i$$
   An activity is **Critical** if $\text{Slack}_i = 0$.
8. **Project Completion Probability (Central Limit Theorem):**
   $$Z = \frac{D - T_{\text{project}}}{\sqrt{\sum_{k \in \text{Critical Path}} \sigma_k^2}}$$
   $$P(T \le D) = \Phi(Z) = \frac{1}{2} \left[ 1 + \text{erf}\left(\frac{Z}{\sqrt{2}}\right) \right]$$

---

## 3. Directory Structure

```
├── app.py                      # Flask Application Controller & Security Headers
├── pert_engine.py              # PERT/CPM Mathematical Computation Engine & DAG Validator
├── test_pert.py                # 12 Automated Unit Tests (Hand-Calculated Benchmarks)
├── requirements.txt            # Minimal Pinned Dependencies
├── Dockerfile                  # Multi-Stage, Non-Root Hardened Container
├── .dockerignore               # Docker Build Exclusions
├── .gitignore                  # Git Version Control Exclusions
├── docker-compose.jenkins.yml  # Local Jenkins & SonarQube Deployment Stack
├── Jenkinsfile                 # Declarative CI/CD Multi-Stage Pipeline
├── sonar-project.properties    # SonarQube Scanner Static Analysis Properties
├── templates/
│   ├── index.html              # Main Dashboard (CRUD Table, Metrics & Visualizer)
│   └── sdg.html                # SDG 9 and SDG 11 Technical Alignment Page
├── static/
│   ├── css/style.css           # Custom Dark Slate Theme & UI System
│   └── js/app.js               # Dynamic Client Logic, SVG Network & Gantt Engine
└── terraform/                  # Infrastructure as Code (AWS Free Tier)
    ├── main.tf                 # EC2, Security Groups & Data Sources
    ├── variables.tf            # Configurable AWS Parameters (ap-south-1)
    ├── outputs.tf              # Public IP & Web Access Endpoint
    ├── versions.tf             # Provider Constraints & Project Tags
    └── user_data.sh            # Automated Cloud-Init Docker Provisioner
```

---

## 4. Local Setup and Execution (Ubuntu 22.04 / WSL2)

### Step 1: Create Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Run Automated Unit Tests (12 Tests)
```bash
python -m unittest -v test_pert.py
# Or using pytest:
pytest -v test_pert.py
```
*Expected Output:*
```
test_01_hand_calculation_case_linear ... ok
test_02_hand_calculation_diamond_slack ... ok
test_03_parallel_critical_paths ... ok
test_04_cycle_detection_error ... ok
...
Ran 12 tests in 0.003s
OK
```

### Step 3: Launch Local Web Server
```bash
python app.py
```
*Expected Output:*
```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```
Open your browser at `http://localhost:5000`.

---

## 5. Security Controls Implemented

- **Non-Root Execution:** Container runs strictly as system user `appuser` (`UID 10001`).
- **Input Sanitization & Validation:** Strict mathematical bounds checking ($O \le M \le P$, $O > 0$), topological cycle detection (3-color DFS), and reference verification.
- **Request Size Limiting:** Payload cap enforced at 1MB (`MAX_CONTENT_LENGTH = 1048576`).
- **Security Response Headers:** `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`.
- **Zero-Secret Codebase:** All environment credentials, AWS keys, and passwords managed externally through environment variables and Jenkins Credentials Binding.
