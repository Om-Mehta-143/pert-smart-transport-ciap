# PERT & Critical Path Analysis for Smart Transportation
## DevSecOps CIAP Microproject Presentation
**Presenter:** Om Vivek Mehta | Roll: TYCS_25 | PRN: 124BTCS1021  
**Class:** Third Year B.Tech (Cybersecurity) | Academic Year 2026–2027  
**Department:** Computer Engineering / Cybersecurity  
**Institute:** Shah & Anchor Kutchhi Engineering College (SAKEC), Chembur, Mumbai  
**Course Outcomes:** CO6 (DevSecOps CI/CD Automation) | **PSO:** PSO2 (Security-First Infrastructure)  
**UN SDGs:** Primary: SDG 9 (Industry, Innovation & Infrastructure) | Supporting: SDG 11 (Sustainable Cities)  

---

## SLIDE 1: TITLE & CANDIDATE CREDENTIALS

### Visual Content:
- **Title:** Cloud-Native PERT & Critical Path Analysis Platform for Urban Smart Transportation
- **Subtitle:** Automated DevSecOps Pipeline with SAST, SCA, Multi-Stage Containerization & Infrastructure as Code
- **Candidate:** Om Vivek Mehta (Roll No: TYCS_25 | PRN: 124BTCS1021)
- **Institution:** Shah & Anchor Kutchhi Engineering College (SAKEC), Mumbai
- **Project Badges:**
  - `Docker Hub: jinwooarise/pert-smart-transport:1.0.0`
  - `Jenkins: 100% Green (Build #8)`
  - `SonarQube: Quality Gate Passed (0 Bugs / 0 Vulns)`
  - `SDG 9 & SDG 11 Aligned`

### Speaker Notes:
> "Respected evaluators and peers, good morning. My name is Om Vivek Mehta, Roll TYCS_25, PRN 124BTCS1021, from the Department of Cybersecurity at Shah & Anchor Kutchhi Engineering College. Today, I am presenting my DevSecOps Continuous Integration, Automation, and Protection (CIAP) Microproject. My project focuses on 'PERT and Critical Path Analysis for a Smart Transportation Application', achieving Course Outcome 6 and Program Specific Outcome 2, directly aligned with United Nations Sustainable Development Goals 9 and 11."

---

## SLIDE 2: PROBLEM STATEMENT & SUSTAINABILITY (SDG 9 & 11)

### Visual Content:
- **The Challenge:** Metropolitan transit development (metro corridors, electric bus transit routes, automated signaling) faces severe delays and cost overruns due to deterministic, single-estimate scheduling.
- **Why PERT?** Traditional CPM fails under uncertainty. PERT's 3-point stochastic model (Optimistic, Most Likely, Pessimistic) models real-world civil and logistical variability.
- **DevSecOps Imperative:** Project management platforms in public infrastructure are high-value targets; they require automated, shift-left vulnerability mitigation, non-root container isolation, and reproducible infrastructure.
- **SDG Mapping:**
  - **SDG 9.1:** Resilient, reliable transport infrastructure through scientific timeline forecasting.
  - **SDG 11.2:** Accelerating affordable, sustainable urban mobility by eliminating execution bottlenecks.

### Speaker Notes:
> "Large-scale urban transportation projects frequently encounter supply chain delays, monsoon disruptions, and regulatory clearances that render traditional, single-duration CPM schedules obsolete. Our platform implements the Program Evaluation and Review Technique, incorporating three-point estimation into a Beta distribution to provide probabilistic completion confidence. Simultaneously, because public infrastructure tools demand high integrity, we engineered this application with a shift-left DevSecOps mindset—enforcing automated security testing at every commit to prevent vulnerabilities from ever reaching production."

---

## SLIDE 3: MATHEMATICAL ENGINE & ARCHITECTURAL DESIGN

### Visual Content:
- **Key PERT Formulations:**
  - Expected Task Duration: $t_e = \frac{a + 4m + b}{6}$
  - Task Variance: $\sigma^2 = \left(\frac{b - a}{6}\right)^2$
  - Slack Calculation: $S_i = LS_i - ES_i = LF_i - EF_i$
  - Z-Score Milestone Probability: $Z = \frac{T_s - T_e}{\sqrt{\sum_{CP} \sigma^2}}$
- **Architectural Highlights:**
  - **Directed Acyclic Graph (DAG) Engine:** Three-color DFS algorithm detecting cyclic dependency deadlocks.
  - **Float Precision Guarantee:** Internal 64-bit float math, rounding strictly at display formatting ($5.5556$ benchmark).
  - **Application Stack:** Python Flask backend with 1MB payload ceiling, CSP headers, responsive Vanilla CSS/JS UI with dynamic SVG AON and Gantt visualizers.

### Speaker Notes:
> "Slide 3 illustrates the core mathematical engine and three-tier architecture. In `pert_engine.py`, we implement topological sorting and a three-color depth-first search to ensure the activity network is a valid Directed Acyclic Graph. The forward pass computes early start and finish times, while the backward pass computes late times and identifies zero-slack tasks. We pay strict attention to numeric stability: variance calculations along the critical path retain complete float precision before rounding to 4 decimals, benchmarked against an exact test assertion of 5.5556."

---

## SLIDE 4: THE AUTOMATED 9-STAGE CI/CD PIPELINE

### Visual Content:
- **Pipeline Flowchart:**
  `Checkout SCM` ➔ `Env Validation` ➔ `Unit Testing (13 Tests)` ➔ `SonarQube SAST` ➔ `Trivy Filesystem Scan` ➔ `Multi-Stage Docker Build` ➔ `Trivy Image Scan` ➔ `Docker Hub Push` ➔ `Production Deploy & Health Check`
- **Pipeline Engine:** Declarative `Jenkinsfile` orchestrating local Jenkins container (`port 8080`).
- **Build Metric:** **Build #8: 100% SUCCESS (Green)** in under 35 seconds.

### Speaker Notes:
> "Our delivery mechanism is governed by an automated 9-stage declarative Jenkins pipeline. Every commit triggers automated environment validation, executes our 13 unit tests, runs static analysis via SonarQube, performs Software Composition Analysis via Trivy, builds a multi-stage Docker image, scans the final image layers for CVEs, pushes the verified tag to Docker Hub, and completes automated deployment with health validation. Build #8 executed flawlessly across all 9 stages in just 35 seconds."

---

## SLIDE 5: SECURITY ASSESSMENT & VULNERABILITY MITIGATION

### Visual Content:
| Scan / Tool | Target | Result / Remediation |
| :--- | :--- | :--- |
| **SonarQube SAST** | Python Codebase & Flask routes | **Quality Gate: PASSED** (0 Bugs, 0 Vulns, 0 Hotspots) |
| **Trivy SCA** | `requirements.txt` dependencies | **0 Vulnerabilities** (Clean Flask 3.0.3 / Werkzeug 3.0.3) |
| **Trivy Image** | `jinwooarise/pert-smart-transport:1.0.0` | **0 App Vulns** (Minimal Debian 12 slim layers) |
| **Docker Hardening** | Container Runtime | **Non-root user `UID 10001 (appuser)`**, no root escalation |
| **HTTP Hardening** | Flask Web Server | **1MB Payload Limit, CSP, nosniff, DENY X-Frame** |

### Speaker Notes:
> "Security is not an afterthought in this project; it is enforced systematically. In SonarQube, our static analysis achieved a clean Quality Gate with zero bugs, code smells, or security hotspots. Trivy filesystem scanning audited our dependencies and confirmed zero CVEs. Furthermore, our Dockerfile incorporates multi-stage builds and drops privileges to a dedicated non-root user with UID 10001, effectively neutralizing container escape risks. Application-level protections cap request bodies at 1 Megabyte to prevent memory exhaustion attacks."

---

## SLIDE 6: INFRASTRUCTURE AS CODE & ENTERPRISE AWS GOVERNANCE

### Visual Content:
- **Terraform Declarations:** Modular AWS IaC (`versions.tf`, `variables.tf`, `main.tf`, `outputs.tf`, `user_data.sh`).
- **Target Architecture:** AWS Mumbai (`ap-south-1`) VPC, public subnet, Internet Gateway, security groups, and automated EC2 bootstrapping.
- **Enterprise Finding (SCP Analysis):**
  - **AWS Organization:** `o-hd66dshcxi`
  - **Enforcing Policy:** Service Control Policy `p-09ktjv95`
  - **Finding:** Programmatic creation of standalone EC2 instances was explicitly denied by parent institutional governance.
  - **DevSecOps Outcome:** Documented multi-tenant governance compliance while verifying production container runtime locally on port 5000.

### Speaker Notes:
> "On Slide 6, we examine our Infrastructure as Code implementation. We codified the target cloud environment using HashiCorp Terraform for AWS region ap-south-1. During the deployment phase, an interesting real-world enterprise phenomenon occurred: our AWS account operates under an institutional AWS Organization with Service Control Policy p-09ktjv95, which explicitly enforces a deny rule on programmatic EC2 instance provisioning. Rather than attempting to bypass these guardrails, we documented this multi-tenant governance behavior—a core competency in enterprise DevSecOps where administrative boundaries and budget controls must be strictly respected."

---

## SLIDE 7: LIVE SYSTEM DEMONSTRATION & VERIFICATION

### Visual Content:
- **Interactive UI Capabilities:**
  - Real-time tabular editing of transit construction activities.
  - Dynamic Activity-on-Node (AON) graph highlighting dual critical paths in vivid red.
  - Responsive Gantt chart with early/late timelines.
  - Target milestone probability calculator ($P(T \le T_s)$).
- **Runtime Verification:**
  - Container `pert-app-prod` active on `http://localhost:5000`.
  - Continuous `/health` monitor confirming `status: healthy`, `uptime`, and memory state.

### Speaker Notes:
> "Moving to the live system demonstration: the user interface allows municipal transit planners to input project tasks, dependencies, and three-point estimates. Upon calculation, the system instantly renders an interactive Activity-on-Node network diagram and a Gantt timeline, clearly highlighting the dual critical paths. Planners can enter a target milestone duration to obtain the exact statistical probability of timely completion. The application actively polls its own `/health` endpoint, ensuring high availability and transparency."

---

## SLIDE 8: CONCLUSION, REFLECTION & FUTURE ROADMAP

### Visual Content:
- **Achievements:**
  - Accurate, dual-critical path PERT engine with benchmarked float precision ($5.5556$).
  - 100% automated 9-stage DevSecOps CI/CD pipeline (Jenkins, SonarQube, Trivy).
  - Multi-stage non-root container deployed to Docker Hub (`jinwooarise/pert-smart-transport`).
  - Formal documentation of enterprise AWS SCP cloud governance.
- **Future Enhancements:**
  - Kubernetes Helm deployment with Horizontal Pod Autoscaling (HPA).
  - Monte Carlo simulation engine (10,000+ stochastic iterations).
  - GitOps automated synchronization via ArgoCD.
- **Open for Questions!**

### Speaker Notes:
> "In conclusion, this CIAP Microproject successfully delivered an end-to-end cloud-native PERT scheduling platform underpinned by an automated, shift-left DevSecOps delivery pipeline. We achieved our objectives across mathematical precision, zero-vulnerability container delivery, and enterprise governance compliance. In the future, we plan to extend this platform into Kubernetes with GitOps synchronization via ArgoCD and multi-iteration Monte Carlo simulations. Thank you for your time, and I now welcome any questions."
