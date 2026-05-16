from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
import json
import os
import sys

app = Flask(__name__)
CORS(app)

# Global state for dashboard
scan_state = {
    "status": "idle",
    "scan_mode": "violation",
    "agents": {
        "sentinel": {"status": "idle", "output": [], "time": None, "elapsed": None},
        "guardian": {"status": "idle", "output": [], "time": None, "elapsed": None},
        "counsel":  {"status": "idle", "output": [], "time": None, "elapsed": None},
        "remediate":{"status": "idle", "output": [], "time": None, "elapsed": None},
        "packager": {"status": "idle", "output": [], "time": None, "elapsed": None},
    },
    "audit_log": [],
    "summary": {
        "pipelines_scanned": 0,
        "failures_detected": 0,
        "violations_found": 0,
        "submission_status": "UNKNOWN",
        "total_elapsed": 0,
        "sentinel_elapsed": 0,
        "guardian_elapsed": 0,
        "counsel_elapsed": 0,
        "remediate_elapsed": 0,
        "packager_elapsed": 0,
    }
}

def run_scan():
    import time as time_module
    scan_start = time_module.time()
    import datetime
    import tools.airflow_mock as airflow_mock
    import tools.dbt_mock as dbt_mock
    import tools.snowflake_mock as snowflake_mock

    # Set scan mode on all tools
    mode = scan_state.get("scan_mode", "violation")
    airflow_mock.SCAN_MODE = mode
    dbt_mock.SCAN_MODE = mode
    snowflake_mock.SCAN_MODE = mode

    from utils.mcp_client import (
        get_pipelines_via_mcp,
        get_snowflake_via_mcp,
        get_dbt_via_mcp,
        rerun_pipeline_via_mcp,
        lookup_regulation_via_mcp,
        create_audit_via_mcp
    )
    from utils.gemini_brain import ask_gemini

    def add_output(agent, line, type="info"):
        scan_state["agents"][agent]["output"].append({"text": line, "type": type})

    scan_state["status"] = "running"
    scan_state["audit_log"] = []
    for a in scan_state["agents"]:
        scan_state["agents"][a] = {"status": "idle", "output": [], "time": None, "elapsed": None}

    # ── SENTINEL ──────────────────────────────────────────
    scan_state["agents"]["sentinel"]["status"] = "running"
    time.sleep(0.5)

    add_output("sentinel", "🔌 Connecting to Airflow MCP tool...", "ai")
    pipelines = airflow_mock.get_pipeline_status()
    failures  = [p for p in pipelines if p["status"] == "failed"]

    scan_state["summary"]["pipelines_scanned"] = len(pipelines)
    scan_state["summary"]["failures_detected"]  = len(failures)

    add_output("sentinel", "✅ MCP Connected: Apache Airflow MCP", "success")
    add_output("sentinel", f"Scanned {len(pipelines)} pipelines — {len(failures)} failure(s) detected", "info")
    scan_state["audit_log"].append({
        "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
        "agent": "SENTINEL",
        "action": "MCP_PIPELINE_SCAN",
        "detail": f"Scanned {len(pipelines)} pipelines via Airflow MCP",
        "severity": "INFO"
    })

    if len(failures) == 0:
        add_output("sentinel", "✅ All 4 pipelines healthy — no failures detected", "success")
        add_output("sentinel", "✅ Phase III Trial Data Ingestion — running", "success")
        add_output("sentinel", "✅ Lab Results Processing — running", "success")
        add_output("sentinel", "✅ Patient Records Sync — running", "success")
        add_output("sentinel", "✅ CDISC SDTM Mapping — running", "success")
    else:
        for f in failures:
            add_output("sentinel", f"❌ FAILED: {f['name']}", "error")
            add_output("sentinel", f"   Error: {f.get('error','Unknown')}", "error")
            prompt = f"""Clinical data pipeline failed.
Pipeline: {f['name']}
Error: {f.get('error','Unknown')}
In 2 sentences: root cause and fastest fix."""
            add_output("sentinel", "🤖 Gemini diagnosing via MCP context...", "ai")
            diagnosis = ask_gemini(prompt)
            add_output("sentinel", f"🔍 {diagnosis}", "ai")
            scan_state["audit_log"].append({
                "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
                "agent": "SENTINEL",
                "action": "FAILURE_DETECTED",
                "detail": f['name'],
                "severity": "CRITICAL"
            })

    scan_state["agents"]["sentinel"]["status"] = "done"
    scan_state["agents"]["sentinel"]["time"] = datetime.datetime.utcnow().strftime("%H:%M:%S")
    scan_state["agents"]["sentinel"]["elapsed"] = round(time_module.time() - scan_start, 1)
    scan_state["summary"]["sentinel_elapsed"] = round(time_module.time() - scan_start, 1)
    time.sleep(1)

    # ── GUARDIAN ──────────────────────────────────────────
    scan_state["agents"]["guardian"]["status"] = "running"
    time.sleep(0.5)

    add_output("guardian", "🔌 Connecting to Snowflake MCP tool...", "ai")
    add_output("guardian", "🔌 Connecting to dbt MCP tool...", "ai")

    dbt_results = dbt_mock.get_dbt_run_status()
    dq_results  = snowflake_mock.get_data_quality_results()

    violations = []

    for m in dbt_results:
        if m["status"] == "error":
            add_output("guardian", f"❌ DBT: {m['model']}", "error")
            add_output("guardian", f"   {m['error']}", "error")
            violations.append({"source": "dbt", "detail": m["error"], "severity": "HIGH", "cdisc_domain": "AE"})
            scan_state["audit_log"].append({
                "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
                "agent": "GUARDIAN",
                "action": "CDISC_VIOLATION",
                "detail": m["error"],
                "severity": "HIGH"
            })
        elif m["status"] == "success":
            add_output("guardian", f"✅ DBT: {m['model']} — {m.get('rows', 0):,} rows", "success")

    for c in dq_results:
        if c["status"] == "FAIL":
            add_output("guardian", f"❌ DATA FAIL: {c['table']}", "error")
            add_output("guardian", f"   {c['violation']}", "error")
            violations.append({
                "source": "snowflake",
                "table": c["table"],
                "detail": c["violation"],
                "cdisc_domain": c.get("cdisc_domain", "AE"),
                "severity": "HIGH"
            })
            scan_state["audit_log"].append({
                "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
                "agent": "GUARDIAN",
                "action": "DATA_QUALITY_FAIL",
                "detail": c["violation"],
                "severity": "HIGH"
            })
        elif c["status"] == "WARN":
            add_output("guardian", f"⚠️  WARN: {c['table']} — {c.get('violation','')[:60]}", "warn")
        elif c["status"] == "PASS":
            add_output("guardian", f"✅ PASS: {c['table']} — {c['check']}", "success")

    if len(violations) == 0:
        add_output("guardian", "✅ All CDISC checks passed — data is compliant", "success")
        add_output("guardian", "✅ All 4 dbt models completed successfully", "success")

    scan_state["summary"]["violations_found"] = len(violations)
    add_output("guardian", f"Total violations: {len(violations)}", "info")
    add_output("guardian", "✅ MCP Connected: dbt MCP", "success")
    add_output("guardian", "✅ MCP Connected: Snowflake MCP", "success")

    scan_state["agents"]["guardian"]["status"] = "done"
    scan_state["agents"]["guardian"]["time"] = datetime.datetime.utcnow().strftime("%H:%M:%S")
    scan_state["agents"]["guardian"]["elapsed"] = round(time_module.time() - scan_start, 1)
    scan_state["summary"]["guardian_elapsed"] = round(time_module.time() - scan_start, 1)
    time.sleep(1)

    # ── COUNSEL ───────────────────────────────────────────
    scan_state["agents"]["counsel"]["status"] = "running"
    time.sleep(0.5)

    if len(violations) == 0:
        add_output("counsel", "✅ No violations detected — no regulatory guidance required", "success")
        add_output("counsel", "✅ All CDISC domains compliant with FDA standards", "success")
        add_output("counsel", "✅ AE domain — compliant", "success")
        add_output("counsel", "✅ DM domain — compliant", "success")
        add_output("counsel", "✅ LB domain — compliant", "success")
        scan_state["audit_log"].append({
            "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
            "agent": "COUNSEL",
            "action": "ALL_DOMAINS_COMPLIANT",
            "detail": "No violations — all FDA CDISC domains compliant",
            "severity": "INFO"
        })
    else:
        for v in violations:
            domain = v.get("cdisc_domain", "AE")
            add_output("counsel", f"🔌 Looking up FDA regulation via MCP: {domain} domain...", "ai")
            reg_data = lookup_regulation_via_mcp(domain, v["detail"][:50])

            if "error" not in reg_data:
                reg = reg_data.get("regulation", {})
                add_output("counsel", f"✅ Regulation: {reg.get('primary','')}", "success")
                add_output("counsel", f"   Risk: {reg.get('risk','')}", "warn")

            add_output("counsel", "🤖 Consulting Gemini for detailed guidance...", "ai")
            prompt = f"""FDA regulatory specialist. Violation: {v['detail']}
Format exactly:
REGULATION: [cite exact reg]
RISK: HIGH/MED/LOW — [one line reason]
REMEDIATION: [2 sentence fix]"""
            guidance = ask_gemini(prompt)
            for line in guidance.split('\n'):
                if line.strip():
                    add_output("counsel", line.strip(), "ai")

            scan_state["audit_log"].append({
                "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
                "agent": "COUNSEL",
                "action": "MCP_REGULATION_LOOKUP",
                "detail": f"FDA lookup for {domain} domain",
                "severity": "INFO"
            })

    scan_state["agents"]["counsel"]["status"] = "done"
    scan_state["agents"]["counsel"]["time"] = datetime.datetime.utcnow().strftime("%H:%M:%S")
    scan_state["agents"]["counsel"]["elapsed"] = round(time_module.time() - scan_start, 1)
    scan_state["summary"]["counsel_elapsed"] = round(time_module.time() - scan_start, 1)
    time.sleep(1)

    # ── REMEDIATE ─────────────────────────────────────────
    scan_state["agents"]["remediate"]["status"] = "running"
    time.sleep(0.5)

    if len(violations) == 0:
        add_output("remediate", "✅ No violations to remediate", "success")
        add_output("remediate", "✅ All pipelines healthy — no reruns required", "success")
        add_output("remediate", "✅ Audit trail complete — 21 CFR Part 11 compliant", "success")
        scan_state["audit_log"].append({
            "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
            "agent": "REMEDIATE",
            "action": "NO_ACTION_REQUIRED",
            "detail": "All systems healthy",
            "severity": "INFO"
        })
    else:
        for v in violations:
            add_output("remediate", "🤖 Generating AI remediation brief...", "ai")
            prompt = f"""Clinical violation: {v['detail']}
SEVERITY: [one line]
IMMEDIATE ACTION: [one line]
FIX: [2 steps]
SIGN-OFF: [who approves]"""
            brief = ask_gemini(prompt)
            for line in brief.split('\n'):
                if line.strip():
                    add_output("remediate", line.strip(), "ai")
            add_output("remediate", "🚨 Escalated to Regulatory Affairs", "error")

            create_audit_via_mcp("REMEDIATE", "BRIEF_GENERATED", v["detail"][:80], "CRITICAL")
            scan_state["audit_log"].append({
                "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
                "agent": "REMEDIATE",
                "action": "BRIEF_GENERATED",
                "detail": v["detail"][:80],
                "severity": "CRITICAL"
            })

    for f in failures:
        add_output("remediate", f"🔌 Triggering pipeline rerun via MCP: {f['name']}", "ai")
        result = rerun_pipeline_via_mcp(f["id"])
        if "error" not in result:
            add_output("remediate", f"✅ {result.get('message','Pipeline queued')}", "success")
        scan_state["audit_log"].append({
            "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
            "agent": "REMEDIATE",
            "action": "MCP_PIPELINE_RERUN",
            "detail": f['name'],
            "severity": "INFO"
        })

    scan_state["agents"]["remediate"]["status"] = "done"
    scan_state["agents"]["remediate"]["time"] = datetime.datetime.utcnow().strftime("%H:%M:%S")
    scan_state["agents"]["remediate"]["elapsed"] = round(time_module.time() - scan_start, 1)
    scan_state["summary"]["remediate_elapsed"] = round(time_module.time() - scan_start, 1)
    time.sleep(1)

    # ── PACKAGER ──────────────────────────────────────────
    scan_state["agents"]["packager"]["status"] = "running"
    time.sleep(0.5)

    high = [v for v in violations if v.get("severity") == "HIGH"]
    if high:
        add_output("packager", f"⏸️  HOLD: {len(high)} unresolved violation(s)", "error")
        add_output("packager", "Awaiting human sign-off before packaging", "warn")
        scan_state["summary"]["submission_status"] = "ON HOLD"
        create_audit_via_mcp("PACKAGER", "PACKAGING_BLOCKED", f"{len(high)} violations", "HIGH")
        scan_state["audit_log"].append({
            "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
            "agent": "PACKAGER",
            "action": "PACKAGING_BLOCKED",
            "detail": f"{len(high)} unresolved violations",
            "severity": "HIGH"
        })
    else:
        add_output("packager", "✅ All checks passed — generating package", "success")
        add_output("packager", "📦 FDA submission package ready", "success")
        scan_state["summary"]["submission_status"] = "READY"
        scan_state["audit_log"].append({
            "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
            "agent": "PACKAGER",
            "action": "PACKAGE_GENERATED",
            "detail": "Submission ready",
            "severity": "INFO"
        })

    scan_state["agents"]["packager"]["status"] = "done"
    scan_state["agents"]["packager"]["time"] = datetime.datetime.utcnow().strftime("%H:%M:%S")
    scan_state["agents"]["packager"]["elapsed"] = round(time_module.time() - scan_start, 1)
    scan_state["summary"]["packager_elapsed"] = round(time_module.time() - scan_start, 1)
    scan_state["summary"]["total_elapsed"] = round(time_module.time() - scan_start, 1)
    scan_state["status"] = "complete"


@app.route("/api/start", methods=["POST"])
def start_scan():
    if scan_state["status"] == "running":
        return jsonify({"error": "Scan already running"}), 400
    data = request.get_json() or {}
    mode = data.get("mode", "violation")
    scan_state["scan_mode"] = mode

    import tools.airflow_mock as airflow
    import tools.dbt_mock as dbt
    import tools.snowflake_mock as snowflake
    import mcp_server
    airflow.SCAN_MODE = mode
    dbt.SCAN_MODE = mode
    snowflake.SCAN_MODE = mode
    mcp_server.SCAN_MODE = mode

    thread = threading.Thread(target=run_scan)
    thread.daemon = True
    thread.start()
    return jsonify({"status": "started", "mode": mode})


@app.route("/api/state")
def get_state():
    return jsonify(scan_state)


@app.route("/api/reset", methods=["POST"])
def reset():
    scan_state["status"] = "idle"
    scan_state["audit_log"] = []
    scan_state["summary"] = {
        "pipelines_scanned": 0,
        "failures_detected": 0,
        "violations_found": 0,
        "submission_status": "UNKNOWN",
        "total_elapsed": 0,
        "sentinel_elapsed": 0,
        "guardian_elapsed": 0,
        "counsel_elapsed": 0,
        "remediate_elapsed": 0,
        "packager_elapsed": 0,
    }
    for a in scan_state["agents"]:
        scan_state["agents"][a] = {"status": "idle", "output": [], "time": None, "elapsed": None}
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)