/**
 * PERT & Critical Path Analyzer Frontend Logic
 * Implements activity CRUD, validation error dispatching, SVG AON network diagram rendering,
 * Gantt chart generation, and real-time /health endpoint polling.
 */

document.addEventListener("DOMContentLoaded", () => {
    const activityRowsTbody = document.getElementById("activity-rows");
    const btnAddRow = document.getElementById("btn-add-row");
    const btnClear = document.getElementById("btn-clear");
    const btnLoadTransit = document.getElementById("btn-load-transit");
    const btnLoadCiap = document.getElementById("btn-load-ciap");
    const pertForm = document.getElementById("pert-form");
    const errorAlert = document.getElementById("error-alert");
    const resultsSummary = document.getElementById("results-summary");
    const healthPill = document.getElementById("health-pill");

    // Initiate real health probe
    pollSystemHealth();
    setInterval(pollSystemHealth, 30000);

    // Preload default Bus Transit system dataset on first load
    loadSampleDataset("/api/sample/transit");

    // Event Handlers
    btnAddRow.addEventListener("click", () => addActivityRow());
    btnClear.addEventListener("click", () => {
        activityRowsTbody.innerHTML = "";
        addActivityRow();
        hideResults();
        hideError();
    });

    btnLoadTransit.addEventListener("click", () => loadSampleDataset("/api/sample/transit"));
    btnLoadCiap.addEventListener("click", () => loadSampleDataset("/api/sample/ciap"));

    pertForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        hideError();

        const activities = parseTableActivities();
        if (activities.length === 0) {
            showError("Please add at least one activity with valid numeric values.");
            return;
        }

        const deadlineInput = document.getElementById("target-deadline-input").value;
        const payload = {
            activities: activities,
            target_deadline: deadlineInput ? parseFloat(deadlineInput) : null
        };

        try {
            const resp = await fetch("/api/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await resp.json();
            if (!resp.ok || !data.success) {
                showError(data.error || "Computation failed.");
                hideResults();
                return;
            }

            renderResults(data.data, data.probability);
        } catch (err) {
            showError("Network error communicating with the server: " + err.message);
            hideResults();
        }
    });

    // Tab Switching
    document.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach((c) => c.classList.add("hidden"));
            btn.classList.add("active");
            const targetId = btn.getAttribute("data-tab");
            const targetEl = document.getElementById(targetId);
            if (targetEl) targetEl.classList.remove("hidden");
        });
    });

    // --- System Health Probe ---
    async function pollSystemHealth() {
        if (!healthPill) return;
        try {
            const res = await fetch("/health");
            if (res.ok) {
                const data = await res.json();
                healthPill.className = "nav-link status-pill status-healthy";
                healthPill.innerHTML = `<span class="pulse-dot"></span> System: Healthy`;
                healthPill.title = `Service: ${data.service} | Status: ${data.status}`;
            } else {
                healthPill.className = "nav-link status-pill status-degraded";
                healthPill.innerHTML = `<span class="pulse-dot"></span> System: Degraded`;
            }
        } catch {
            healthPill.className = "nav-link status-pill status-offline";
            healthPill.innerHTML = `<span class="pulse-dot"></span> System: Offline`;
        }
    }

    // --- Helper Functions ---

    function showError(msg) {
        errorAlert.textContent = msg;
        errorAlert.classList.remove("hidden");
        errorAlert.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function hideError() {
        errorAlert.classList.add("hidden");
        errorAlert.textContent = "";
    }

    function hideResults() {
        resultsSummary.classList.add("hidden");
    }

    function addActivityRow(data = {}) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><input type="text" class="act-id" value="${data.id || ""}" placeholder="e.g. A" required></td>
            <td><input type="text" class="act-name" value="${data.name || ""}" placeholder="Activity Name"></td>
            <td><input type="text" class="act-preds" value="${(data.predecessors || []).join(", ")}" placeholder="e.g. A, B"></td>
            <td><input type="number" step="0.1" class="act-o" value="${data.optimistic !== undefined ? data.optimistic : ""}" placeholder="O (Days)" required></td>
            <td><input type="number" step="0.1" class="act-m" value="${data.most_likely !== undefined ? data.most_likely : ""}" placeholder="M (Days)" required></td>
            <td><input type="number" step="0.1" class="act-p" value="${data.pessimistic !== undefined ? data.pessimistic : ""}" placeholder="P (Days)" required></td>
            <td><button type="button" class="btn-danger-sm btn-del-row" title="Delete Row">X</button></td>
        `;

        tr.querySelector(".btn-del-row").addEventListener("click", () => {
            if (activityRowsTbody.children.length > 1) {
                tr.remove();
            } else {
                showError("The schedule must contain at least one activity.");
            }
        });

        activityRowsTbody.appendChild(tr);
    }

    function parseTableActivities() {
        const rows = activityRowsTbody.querySelectorAll("tr");
        const activities = [];

        rows.forEach((r) => {
            const idVal = r.querySelector(".act-id").value.trim();
            const nameVal = r.querySelector(".act-name").value.trim();
            const predsVal = r.querySelector(".act-preds").value.trim();
            const oVal = parseFloat(r.querySelector(".act-o").value);
            const mVal = parseFloat(r.querySelector(".act-m").value);
            const pVal = parseFloat(r.querySelector(".act-p").value);

            if (idVal && !isNaN(oVal) && !isNaN(mVal) && !isNaN(pVal)) {
                const preds = predsVal
                    ? predsVal.split(",").map((s) => s.trim()).filter((s) => s.length > 0)
                    : [];

                activities.push({
                    id: idVal,
                    name: nameVal || idVal,
                    predecessors: preds,
                    optimistic: oVal,
                    most_likely: mVal,
                    pessimistic: pVal
                });
            }
        });

        return activities;
    }

    async function loadSampleDataset(url) {
        hideError();
        try {
            const resp = await fetch(url);
            const json = await resp.json();
            if (json.activities) {
                activityRowsTbody.innerHTML = "";
                json.activities.forEach((act) => addActivityRow(act));
                // Automatically run calculation on sample load
                document.getElementById("btn-calculate").click();
            }
        } catch (e) {
            showError("Failed loading sample dataset: " + e.message);
        }
    }

    function renderResults(data, probData) {
        resultsSummary.classList.remove("hidden");

        // Top Metrics (Days unit explicit)
        document.getElementById("val-duration").textContent = Number(data.project_duration).toFixed(2);
        document.getElementById("val-critical-path").textContent = data.critical_path.join(" -> ");
        document.getElementById("val-cp-count").textContent = `${data.critical_paths.length} Critical Path(s) Identified`;
        // Project Variance displayed to 4 decimals (e.g., 5.5556 for transit dataset)
        document.getElementById("val-variance").textContent = Number(data.project_variance).toFixed(4);
        document.getElementById("val-std-dev").textContent = Number(data.project_std_dev).toFixed(4);

        // Probability Box
        const probCard = document.getElementById("prob-card");
        if (probData) {
            probCard.classList.remove("hidden");
            document.getElementById("prob-target").textContent = `${probData.target_deadline} Days`;
            document.getElementById("prob-zscore").textContent = probData.z_score;
            document.getElementById("prob-percent").textContent = `${probData.probability_percent}%`;

            const assumptionsList = document.getElementById("prob-assumptions");
            assumptionsList.innerHTML = "";
            probData.assumptions.forEach((asm) => {
                const li = document.createElement("li");
                li.textContent = asm;
                assumptionsList.appendChild(li);
            });
        } else {
            probCard.classList.add("hidden");
        }

        // Results Table
        const tbody = document.getElementById("results-tbody");
        tbody.innerHTML = "";
        data.activities.forEach((act) => {
            const tr = document.createElement("tr");
            if (act.is_critical) {
                tr.classList.add("critical-row");
            }

            tr.innerHTML = `
                <td><strong>${act.id}</strong></td>
                <td>${act.name}</td>
                <td>${act.predecessors.join(", ") || "-"}</td>
                <td>${act.te.toFixed(2)}</td>
                <td>${act.variance.toFixed(4)}</td>
                <td>${act.es.toFixed(2)}</td>
                <td>${act.ef.toFixed(2)}</td>
                <td>${act.ls.toFixed(2)}</td>
                <td>${act.lf.toFixed(2)}</td>
                <td><strong>${act.slack.toFixed(2)}</strong></td>
                <td>
                    <span class="${act.is_critical ? "badge-critical" : "badge-normal"}">
                        ${act.is_critical ? "CRITICAL" : "NORMAL"}
                    </span>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Visualizations
        renderNetworkDiagram(data);
        renderGanttChart(data);
    }

    function renderNetworkDiagram(data) {
        const container = document.getElementById("network-svg-container");
        container.innerHTML = "";

        const activities = data.activities;
        const actMap = {};
        activities.forEach((a) => (actMap[a.id] = a));

        // Group into topological rank layers based on ES
        const layers = {};
        activities.forEach((a) => {
            const depth = calculateDepth(a.id, actMap);
            if (!layers[depth]) layers[depth] = [];
            layers[depth].push(a);
        });

        const sortedDepths = Object.keys(layers).map(Number).sort((a, b) => a - b);
        const colWidth = 190;
        const rowHeight = 95;
        const startX = 65;
        const startY = 65;

        const nodePositions = {};
        let maxRow = 1;

        sortedDepths.forEach((d, colIdx) => {
            const colActs = layers[d];
            if (colActs.length > maxRow) maxRow = colActs.length;
            colActs.forEach((act, rowIdx) => {
                nodePositions[act.id] = {
                    x: startX + colIdx * colWidth,
                    y: startY + rowIdx * rowHeight,
                    data: act
                };
            });
        });

        const totalWidth = Math.max(840, startX + sortedDepths.length * colWidth + 80);
        const totalHeight = Math.max(300, startY + maxRow * rowHeight + 60);

        let svg = `<svg width="${totalWidth}" height="${totalHeight}" xmlns="http://www.w3.org/2000/svg">`;
        svg += `
            <defs>
                <marker id="arrow-normal" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
                </marker>
                <marker id="arrow-critical" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
                </marker>
            </defs>
        `;

        // Draw dependency arrows
        activities.forEach((act) => {
            const toPos = nodePositions[act.id];
            act.predecessors.forEach((pId) => {
                const fromPos = nodePositions[pId];
                if (fromPos && toPos) {
                    const isCritEdge = act.is_critical && fromPos.data.is_critical;
                    const strokeColor = isCritEdge ? "#ef4444" : "#4b5563";
                    const strokeWidth = isCritEdge ? "3" : "1.5";
                    const marker = isCritEdge ? "url(#arrow-critical)" : "url(#arrow-normal)";

                    svg += `<line x1="${fromPos.x}" y1="${fromPos.y}" x2="${toPos.x}" y2="${toPos.y}" stroke="${strokeColor}" stroke-width="${strokeWidth}" marker-end="${marker}" />`;
                }
            });
        });

        // Draw AON Nodes
        activities.forEach((act) => {
            const pos = nodePositions[act.id];
            const isCrit = act.is_critical;
            const nodeFill = isCrit ? "#7f1d1d" : "#0f3460";
            const strokeColor = isCrit ? "#ef4444" : "#3b82f6";
            const strokeWidth = isCrit ? "2.5" : "1.5";

            svg += `
                <g class="network-node" data-id="${act.id}">
                    <circle cx="${pos.x}" cy="${pos.y}" r="25" fill="${nodeFill}" stroke="${strokeColor}" stroke-width="${strokeWidth}" />
                    <text x="${pos.x}" y="${pos.y - 3}" fill="#ffffff" font-size="12" font-weight="bold" text-anchor="middle" font-family="monospace">${act.id}</text>
                    <text x="${pos.x}" y="${pos.y + 11}" fill="#93c5fd" font-size="9" text-anchor="middle">${act.te.toFixed(1)}d</text>
                    <text x="${pos.x}" y="${pos.y + 38}" fill="${isCrit ? "#fca5a5" : "#cbd5e1"}" font-size="10" text-anchor="middle">${act.name.substring(0, 15)}</text>
                </g>
            `;
        });

        svg += `</svg>`;
        container.innerHTML = svg;
    }

    function calculateDepth(actId, actMap, visited = new Set()) {
        if (visited.has(actId)) return 0;
        visited.add(actId);
        const act = actMap[actId];
        if (!act || !act.predecessors || act.predecessors.length === 0) return 0;
        return 1 + Math.max(...act.predecessors.map((p) => calculateDepth(p, actMap, new Set(visited))));
    }

    function renderGanttChart(data) {
        const container = document.getElementById("gantt-container");
        container.innerHTML = "";

        const activities = data.activities;
        const projectDuration = Math.max(1, data.project_duration);

        activities.forEach((act) => {
            const row = document.createElement("div");
            row.className = "gantt-row";

            const leftPct = (act.es / projectDuration) * 100;
            const widthPct = Math.max(2, (act.te / projectDuration) * 100);

            row.innerHTML = `
                <div class="gantt-label" title="${act.id}: ${act.name}">
                    [${act.id}] ${act.name}
                </div>
                <div class="gantt-track">
                    <div class="gantt-bar ${act.is_critical ? "critical" : "normal"}"
                         style="left: ${leftPct.toFixed(2)}%; width: ${widthPct.toFixed(2)}%;"
                         title="ES: ${act.es}d, EF: ${act.ef}d, Slack: ${act.slack}d">
                        ${act.te.toFixed(1)}d
                    </div>
                </div>
            `;
            container.appendChild(row);
        });
    }
});
