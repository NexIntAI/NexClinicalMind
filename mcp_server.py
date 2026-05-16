"""
NexClinicalMind MCP Server
Exposes clinical data pipeline tools via Model Context Protocol
"""
from mcp.server.fastmcp import FastMCP
import random
import datetime
import json

mcp = FastMCP("NexClinicalMind Pipeline Tools", host="127.0.0.1", port=8000)
SCAN_MODE = "violation"
# ── TOOL 1: Airflow Pipeline Status ───────────────────────
@mcp.tool()
def get_airflow_pipeline_status() -> str:
    """Get real-time status of all clinical trial data pipelines."""
    import tools.airflow_mock as airflow
    airflow.SCAN_MODE = SCAN_MODE
    pipelines = airflow.get_pipeline_status()
    return json.dumps({
        "source": "Apache Airflow MCP",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "scan_mode": SCAN_MODE,
        "total_pipelines": len(pipelines),
        "failed": len([p for p in pipelines if p["status"] == "failed"]),
        "pipelines": pipelines
    })

# ── TOOL 2: Snowflake Data Quality ────────────────────────
@mcp.tool()
def get_snowflake_data_quality() -> str:
    """Run CDISC compliance checks on clinical trial data in Snowflake."""
    import tools.snowflake_mock as snowflake
    snowflake.SCAN_MODE = SCAN_MODE
    checks = snowflake.get_data_quality_results()
    return json.dumps({
        "source": "Snowflake MCP",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "scan_mode": SCAN_MODE,
        "total_checks": len(checks),
        "failed": len([c for c in checks if c["status"] == "FAIL"]),
        "warnings": len([c for c in checks if c["status"] == "WARN"]),
        "checks": checks
    })
# ── TOOL 3: dbt Model Status ───────────────────────────────
@mcp.tool()
def get_dbt_model_status() -> str:
    """Get status of dbt transformation models for CDISC SDTM mapping."""
    import tools.dbt_mock as dbt
    dbt.SCAN_MODE = SCAN_MODE
    models = dbt.get_dbt_run_status()
    return json.dumps({
        "source": "dbt MCP",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "scan_mode": SCAN_MODE,
        "total_models": len(models),
        "failed": len([m for m in models if m["status"] == "error"]),
        "skipped": len([m for m in models if m["status"] == "skipped"]),
        "models": models
    })
# ── TOOL 4: Rerun Pipeline ─────────────────────────────────
@mcp.tool()
def rerun_airflow_pipeline(pipeline_id: str) -> str:
    """
    Trigger a rerun of a failed Airflow pipeline.
    Returns confirmation and estimated completion time.
    
    Args:
        pipeline_id: The unique identifier of the pipeline to rerun
    """
    return json.dumps({
        "source": "Apache Airflow MCP",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "action": "PIPELINE_RERUN_TRIGGERED",
        "pipeline_id": pipeline_id,
        "status": "queued",
        "estimated_completion": "2026-05-10T15:15:00Z",
        "message": f"Pipeline {pipeline_id} successfully queued for rerun"
    })

# ── TOOL 5: FDA Regulation Lookup ─────────────────────────
@mcp.tool()
def lookup_fda_regulation(cdisc_domain: str, violation_type: str) -> str:
    """
    Look up applicable FDA regulations and CDISC standards
    for a specific domain violation. Returns regulation
    citations and remediation requirements.
    
    Args:
        cdisc_domain: CDISC domain code (e.g., AE, DM, LB)
        violation_type: Type of violation detected
    """
    regulations = {
        "AE": {
            "primary": "FDA 21 CFR 312.32 — IND Safety Reports",
            "cdisc": "CDISC SDTM Implementation Guide v3.3 — AE Domain",
            "submission": "FDA Study Data Technical Conformance Guide v5.0",
            "required_vars": ["STUDYID","DOMAIN","USUBJID","AESEQ","AETERM","AESTDTC"],
            "risk": "HIGH — Adverse event data directly impacts patient safety assessment"
        },
        "DM": {
            "primary": "FDA 21 CFR 50 — Protection of Human Subjects",
            "cdisc": "CDISC SDTM Implementation Guide v3.3 — DM Domain",
            "submission": "FDA Study Data Technical Conformance Guide v5.0",
            "required_vars": ["STUDYID","DOMAIN","USUBJID","SUBJID","RFSTDTC","DMDTC"],
            "risk": "HIGH — Demographics data required for population analysis"
        },
        "LB": {
            "primary": "FDA 21 CFR 312.23 — IND Content and Format",
            "cdisc": "CDISC SDTM Implementation Guide v3.3 — LB Domain",
            "submission": "FDA Study Data Technical Conformance Guide v5.0",
            "required_vars": ["STUDYID","DOMAIN","USUBJID","LBSEQ","LBTESTCD","LBORRES"],
            "risk": "MEDIUM — Lab data impacts efficacy and safety analysis"
        },
        "IC": {
            "primary": "FDA 21 CFR Part 50 — Protection of Human Subjects",
            "cdisc": "CDISC SDTM Implementation Guide v3.3 — IC Domain",
            "submission": "FDA Study Data Technical Conformance Guide v5.0",
            "required_vars": ["STUDYID","DOMAIN","USUBJID","ICSEQ","ICDTC","ICVERSION","ICLANG"],
            "risk": "CRITICAL — Missing informed consent can invalidate entire trial and trigger FDA clinical hold"
        }
    }
    reg = regulations.get(cdisc_domain.upper(), regulations["AE"])
    return json.dumps({
        "source": "FDA Regulatory Database MCP",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "cdisc_domain": cdisc_domain.upper(),
        "violation_type": violation_type,
        "regulation": reg
    })

# ── TOOL 6: Generate Audit Entry ──────────────────────────
@mcp.tool()
def create_audit_entry(
    agent: str,
    action: str,
    detail: str,
    severity: str
) -> str:
    """
    Create a 21 CFR Part 11 compliant audit trail entry.
    Logs to the immutable compliance audit system.
    
    Args:
        agent: Name of the agent creating the entry
        action: Action being logged
        detail: Detailed description
        severity: INFO, WARN, HIGH, or CRITICAL
    """
    entry = {
        "source": "NexClinicalMind Audit MCP",
        "audit_id": f"AUD-{random.randint(100000,999999)}",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "agent": agent,
        "action": action,
        "detail": detail,
        "severity": severity,
        "standard": "21 CFR Part 11",
        "system": "NexClinicalMind v1.0",
        "immutable": True
    }
    # Write to audit file
    with open("mcp_audit_trail.json", "a") as f:
        f.write(json.dumps(entry) + "\n")
    return json.dumps(entry)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    mcp = FastMCP("NexClinicalMind Pipeline Tools", host="0.0.0.0", port=port)
    mcp.run(transport="streamable-http")