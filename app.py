"""
Flask Web Application for PERT & Critical Path Analysis
Topic: PERT and Critical Path Analysis for a Smart Transportation Application
SDG Alignment: SDG 9 (Primary) & SDG 11 (Supporting)
Student: Om Vivek Mehta (Roll: TYCS_25, PRN: 124BTCS1021)
Institute: SAKEC (Shah and Anchor Kutchhi Engineering College)
"""

import os
from flask import Flask, render_template, request, jsonify
from pert_engine import PERTEngine, PERTValidationError

app = Flask(__name__)

# Security Hardening: Request Size Limits (1MB maximum payload)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024


@app.after_request
def apply_security_headers(response):
    """Enforce defense-in-depth security response headers."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self';"
    )
    return response


# Sample Datasets
SAMPLE_TRANSIT_PROJECT = [
    {"id": "A", "name": "Requirements & Route Specs", "predecessors": [], "optimistic": 2.0, "most_likely": 4.0, "pessimistic": 6.0},
    {"id": "B", "name": "GPS Module Hardware Proc", "predecessors": ["A"], "optimistic": 3.0, "most_likely": 6.0, "pessimistic": 9.0},
    {"id": "C", "name": "Backend Ingestion API", "predecessors": ["A"], "optimistic": 4.0, "most_likely": 7.0, "pessimistic": 16.0},
    {"id": "D", "name": "Firmware & GPS Testing", "predecessors": ["B"], "optimistic": 2.0, "most_likely": 5.0, "pessimistic": 8.0},
    {"id": "E", "name": "Mobile Rider UI", "predecessors": ["A"], "optimistic": 3.0, "most_likely": 6.0, "pessimistic": 9.0},
    {"id": "F", "name": "Cloud Stream Processor", "predecessors": ["C"], "optimistic": 2.0, "most_likely": 4.0, "pessimistic": 6.0},
    {"id": "G", "name": "System Integration", "predecessors": ["D", "E", "F"], "optimistic": 2.0, "most_likely": 3.0, "pessimistic": 4.0},
    {"id": "H", "name": "Security Audit & PenTest", "predecessors": ["G"], "optimistic": 1.0, "most_likely": 2.0, "pessimistic": 3.0},
    {"id": "I", "name": "Pilot Fleet Rollout", "predecessors": ["H"], "optimistic": 1.0, "most_likely": 3.0, "pessimistic": 5.0},
]

SAMPLE_CIAP_DELIVERY_PLAN = [
    {"id": "T1", "name": "Architecture & Scope Definition", "predecessors": [], "optimistic": 1.0, "most_likely": 2.0, "pessimistic": 3.0},
    {"id": "T2", "name": "Core PERT Engine & Math Tests", "predecessors": ["T1"], "optimistic": 2.0, "most_likely": 3.0, "pessimistic": 4.0},
    {"id": "T3", "name": "Flask Web UI & SVG Visualizer", "predecessors": ["T2"], "optimistic": 2.0, "most_likely": 4.0, "pessimistic": 6.0},
    {"id": "T4", "name": "Dockerfile & Non-Root Hardening", "predecessors": ["T3"], "optimistic": 1.0, "most_likely": 2.0, "pessimistic": 3.0},
    {"id": "T5", "name": "Jenkins CI/CD Pipeline Setup", "predecessors": ["T4"], "optimistic": 2.0, "most_likely": 3.0, "pessimistic": 4.0},
    {"id": "T6", "name": "SonarQube & Trivy Scan Hardening", "predecessors": ["T5"], "optimistic": 2.0, "most_likely": 3.0, "pessimistic": 4.0},
    {"id": "T7", "name": "Terraform AWS Free Tier Config", "predecessors": ["T5"], "optimistic": 2.0, "most_likely": 3.0, "pessimistic": 4.0},
    {"id": "T8", "name": "Integration & Cloud Verification", "predecessors": ["T6", "T7"], "optimistic": 1.0, "most_likely": 2.0, "pessimistic": 3.0},
    {"id": "T9", "name": "Academic Report & PPT Drafting", "predecessors": ["T8"], "optimistic": 3.0, "most_likely": 5.0, "pessimistic": 7.0},
    {"id": "T10", "name": "Video Demo & Final QA Audit", "predecessors": ["T9"], "optimistic": 1.0, "most_likely": 2.0, "pessimistic": 3.0},
]


@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("index.html")


@app.route("/sdg")
def sdg():
    """SDG 9 & SDG 11 mapping page."""
    return render_template("sdg.html")


@app.route("/health")
@app.route("/healthz")
def health():
    """Liveness and readiness health probe for UI badge, Docker, and AWS ALB."""
    return jsonify({
        "status": "healthy",
        "service": "pert-smart-transport-ciap",
        "precision": "full_float_precision"
    }), 200


@app.route("/api/sample/transit")
def sample_transit():
    """Returns the default smart transportation dataset."""
    return jsonify({"activities": SAMPLE_TRANSIT_PROJECT})


@app.route("/api/sample/ciap")
def sample_ciap():
    """Returns the 3-day CIAP Microproject schedule dataset."""
    return jsonify({"activities": SAMPLE_CIAP_DELIVERY_PLAN})


@app.route("/api/calculate", methods=["POST"])
def calculate():
    """
    Accepts activity list, validates schema and DAG properties,
    and returns full CPM/PERT results.
    """
    data = request.get_json(silent=True)
    if not data or "activities" not in data:
        return jsonify({"error": "Invalid request. JSON body must contain 'activities' list."}), 400

    activities = data["activities"]
    if not isinstance(activities, list):
        return jsonify({"error": "'activities' must be an array."}), 400

    try:
        engine = PERTEngine(activities)
        summary = engine.compute()

        # Optional probability calculation if target deadline supplied
        target_deadline = data.get("target_deadline")
        prob_data = None
        if target_deadline is not None:
            try:
                td = float(target_deadline)
                if td > 0:
                    prob_data = engine.calculate_probability(td)
            except ValueError:
                pass

        return jsonify({
            "success": True,
            "data": summary,
            "probability": prob_data
        }), 200

    except PERTValidationError as pe:
        return jsonify({"success": False, "error": str(pe)}), 422
    except Exception as e:
        return jsonify({"success": False, "error": f"Internal computation error: {str(e)}"}), 500


@app.route("/api/probability", methods=["POST"])
def probability():
    """Endpoint for calculating deadline completion probability on existing activity sets."""
    data = request.get_json(silent=True)
    if not data or "activities" not in data or "target_deadline" not in data:
        return jsonify({"error": "Request must include 'activities' and 'target_deadline'."}), 400

    try:
        td = float(data["target_deadline"])
        if td <= 0:
            return jsonify({"error": "Target deadline must be positive."}), 400

        engine = PERTEngine(data["activities"])
        engine.compute()
        prob_res = engine.calculate_probability(td)
        return jsonify({"success": True, "probability": prob_res}), 200
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid target_deadline format."}), 400
    except PERTValidationError as pe:
        return jsonify({"success": False, "error": str(pe)}), 422


if __name__ == "__main__":
    # Host on 0.0.0.0 and port 5000 for standard local and container execution
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
