# DEVSECOPS DEMO VIDEO SCRIPT & SECRETS HYGIENE CHECKLIST
## Project: PERT and Critical Path Analysis for Smart Transportation
**Student:** Om Vivek Mehta | Roll: TYCS_25 | PRN: 124BTCS1021  
**Target Video Duration:** 5 to 7 Minutes  
**Target Audience:** Evaluators, Professors, and DevSecOps Engineers  

---

# PART 1: PRE-RECORDING SECRETS HYGIENE CHECKLIST

Before hitting "Record" on OBS or your screen recorder, perform this mandatory 6-point audit:

- [ ] **Check 1: Clean Terminal Environment:** Close any PowerShell or CMD windows displaying previous AWS Secret Access Keys or Docker login passwords. Open a fresh terminal tab.
- [ ] **Check 2: Browser Tabs & History:** Close all personal tabs. Ensure open browser tabs are strictly:
  - `http://localhost:5000` (PERT Application)
  - `http://localhost:8080/job/pert-smart-transport-pipeline/` (Jenkins)
  - `http://localhost:9000/dashboard?id=pert-smart-transport` (SonarQube)
  - `https://hub.docker.com/r/jinwooarise/pert-smart-transport` (Docker Hub)
  - `https://github.com/Om-Mehta-143/pert-smart-transport-ciap` (GitHub)
- [ ] **Check 3: AWS Console / CLI Session:** Ensure no IAM user credential credentials or `.env` files are open in VS Code.
- [ ] **Check 4: IDE Workspace:** Close all `.env`, `.terraform.lock.hcl`, and state files in VS Code. Keep `pert_engine.py`, `Dockerfile`, and `Jenkinsfile` ready.
- [ ] **Check 5: Health Check Verified:** Verify `curl http://localhost:5000/health` returns `{"status":"healthy"}` before recording.
- [ ] **Check 6: Microphone & Audio Level:** Perform a 10-second test recording to ensure clear audio without clipping or heavy background fan noise.

---

# PART 2: 5-TO-7 MINUTE TIMESTAMPED VIDEO SCRIPT

### `00:00 - 00:45` | Segment 1: Introduction & Project Motivation
- **On Screen:** Title slide or Web Application Dashboard (`http://localhost:5000`).
- **Spoken Audio:**
  > "Hello everyone. My name is Om Vivek Mehta, Roll TYCS_25, PRN 124BTCS1021, Third Year B.Tech Cybersecurity student at Shah & Anchor Kutchhi Engineering College. Today, I am demonstrating my DevSecOps CIAP Microproject: 'PERT and Critical Path Analysis for a Smart Transportation Application'. This project fulfills Course Outcome 6 and PSO2, addressing UN Sustainable Development Goal 9 for resilient infrastructure and SDG 11 for sustainable urban transit. We combine advanced stochastic project scheduling with a fully automated, shift-left DevSecOps delivery pipeline."

### `00:45 - 01:45` | Segment 2: Web Platform & PERT Calculation Engine
- **On Screen:** Web Application at `http://localhost:5000`. Show the task input table, click "Calculate Schedule", scroll through the AON Network Diagram and Gantt chart.
- **Spoken Audio:**
  > "Here is our running web application. Transportation infrastructure projects—like metro lines and smart charging networks—suffer from high duration variance. Unlike deterministic CPM, our engine accepts three-point estimates: optimistic, most likely, and pessimistic times. 
  > 
  > When I click 'Calculate Schedule', the Python backend executes a three-color DFS cycle check, topological sorting, forward and backward passes. It identifies the dual critical paths highlighted in vivid red. We maintain unrounded 64-bit float precision across all variances, benchmarked to an exact test assertion of 5.5556. Planners can also input target milestone days to determine completion probability using the normal distribution cumulative function."

### `01:45 - 02:45` | Segment 3: Codebase & Automated Unit Testing
- **On Screen:** VS Code showing `pert_engine.py` and `test_pert.py`. Open terminal and run: `python -m unittest test_pert.py -v`.
- **Spoken Audio:**
  > "Turning to the codebase: `pert_engine.py` is written purely in Python without external mathematical dependencies, keeping our container attack surface minimal. In `test_pert.py`, we authored 13 unit tests covering cycle detection, disconnected topologies, expected duration math, and float precision assertions.
  > 
  > Running `python -m unittest test_pert.py -v` demonstrates that all 13 tests execute in under 0.05 seconds with zero failures."

### `02:45 - 04:00` | Segment 4: 9-Stage Automated Jenkins CI/CD Pipeline
- **On Screen:** Jenkins UI at `http://localhost:8080/job/pert-smart-transport-pipeline/8/`. Click into Stage View for Build #8.
- **Spoken Audio:**
  > "Now, let us examine the core DevSecOps automation. Here is our Jenkins pipeline running inside a local Docker environment. Build #8 executed across 9 declarative stages and is completely GREEN.
  > 
  > - Stage 1 checks out the Git repository.
  > - Stage 2 validates the runtime environment.
  > - Stage 3 executes our automated test suite.
  > - Stage 4 triggers Static Application Security Testing via SonarQube on port 9000.
  > - Stage 5 runs Trivy Software Composition Analysis on our dependencies, finding 0 vulnerabilities.
  > - Stage 6 builds our multi-stage Docker image using Python 3.11-slim.
  > - Stage 7 runs Trivy Image scanning on the compiled container layers.
  > - Stage 8 tags and pushes the artifact to Docker Hub.
  > - Stage 9 deploys the container `pert-app-prod` and performs automated health validation. The entire pipeline executes in under 35 seconds."

### `04:00 - 04:50` | Segment 5: Security Auditing (SonarQube & Trivy)
- **On Screen:** SonarQube Dashboard at `http://localhost:9000/dashboard?id=pert-smart-transport` and Docker Hub at `https://hub.docker.com/r/jinwooarise/pert-smart-transport`.
- **Spoken Audio:**
  > "Opening SonarQube, our project achieves a clean 'PASSED' Quality Gate with 0 bugs, 0 vulnerabilities, 0 security hotspots, and 0.0% duplication. In our Dockerfile, we enforce least privilege by creating a dedicated non-root user with UID 10001, preventing container breakout attacks. The resulting image is pushed to Docker Hub under `jinwooarise/pert-smart-transport` with a compressed size of only 53.6 megabytes."

### `04:50 - 05:45` | Segment 6: Terraform IaC & Enterprise AWS Governance
- **On Screen:** VS Code showing `terraform/main.tf` and the decoded AWS Authorization failure notes.
- **Spoken Audio:**
  > "For cloud infrastructure, we codified our AWS environment using Terraform. When applying this in our AWS account, we encountered an authentic enterprise governance event: the AWS organization enforced Service Control Policy p-09ktjv95, which denies programmatic EC2 creation to prevent rogue billing. 
  > 
  > As DevSecOps engineers, understanding and respecting enterprise cloud governance and organizational guardrails is just as important as writing code. We documented this finding thoroughly in Section 8 and verified production deployment on our local Docker container runtime."

### `05:45 - 06:15` | Segment 7: Conclusion & Wrap-Up
- **On Screen:** Web Application showing the `/health` endpoint output `{"status":"healthy","uptime_seconds":...}`.
- **Spoken Audio:**
  > "To verify, our production container is actively responding with HTTP 200 and healthy status. In summary, this project combines stochastic mathematical modeling for sustainable transportation with an enterprise-grade DevSecOps pipeline adhering to zero-vulnerability standards. Thank you for watching!"

---

# PART 3: PROFESSIONAL LINKEDIN POST CAPTION

```text
🚀 Excited to share my DevSecOps CIAP Microproject: Cloud-Native PERT & Critical Path Analysis for Smart Transportation Networks!

As part of my Third Year B.Tech in Cybersecurity at Shah & Anchor Kutchhi Engineering College (SAKEC), I designed and automated an end-to-end, shift-left DevSecOps delivery pipeline for urban transit project scheduling.

🏙️ The Core Problem & SDG Alignment:
Urban transportation projects (metro corridors, EV fleet charging infrastructure, smart signaling) often face severe delays due to deterministic scheduling. By integrating the Program Evaluation and Review Technique (PERT) with 3-point stochastic estimation (a, m, b) into a Beta distribution, our platform calculates dual critical paths and milestone completion probabilities, directly supporting #SDG9 (Industry & Infrastructure) and #SDG11 (Sustainable Cities).

🔐 DevSecOps Pipeline Highlights:
✅ 9-Stage Declarative Jenkins Pipeline: Automated from code checkout to production health check.
✅ Shift-Left Security: Integrated SonarQube SAST (0 bugs, 0 vulnerabilities, 0 hotspots) and Trivy SCA/Container scanning.
✅ Multi-Stage Hardened Docker Build: Lightweight 53.6 MB image executed strictly under non-root UID 10001 to prevent container breakouts.
✅ Automated Test Suite: 13 unit tests validating graph acyclicity (3-color DFS) and precision benchmarks (5.5556 variance assertion).
✅ Infrastructure as Code (IaC): Terraform templates for AWS ap-south-1 with enterprise Service Control Policy (SCP) governance analysis.

📦 Artifacts:
• GitHub: https://github.com/Om-Mehta-143/pert-smart-transport-ciap
• Docker Hub: https://hub.docker.com/r/jinwooarise/pert-smart-transport

Grateful to my professors and mentors at SAKEC for guiding me on this journey!

#DevSecOps #Cybersecurity #Jenkins #Docker #SonarQube #Trivy #Terraform #AWS #Python #Flask #CloudComputing #SDG9 #SDG11 #SAKEC #StudentProject #Engineering
```
