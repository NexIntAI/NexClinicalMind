from tools.dbt_mock import get_dbt_run_status
from tools.snowflake_mock import get_data_quality_results
from utils.audit_log import log_event

def run_guardian():
    print("\n" + "="*60)
    print("  GUARDIAN AGENT — CDISC Compliance Validator")
    print("="*60)

    dbt_results = get_dbt_run_status()
    dq_results  = get_data_quality_results()
    violations  = []

    # Check dbt models
    for model in dbt_results:
        if model["status"] == "error":
            print(f"\n  ❌ DBT VIOLATION: {model['model']}")
            print(f"     Error: {model['error']}")
            violations.append({"source": "dbt", "model": model["model"], "detail": model["error"]})
            log_event("GUARDIAN", "CDISC_VIOLATION", model["error"], "HIGH")

    # Check Snowflake data quality
    for check in dq_results:
        if check["status"] == "FAIL":
            print(f"\n  ❌ DATA QUALITY FAIL: {check['table']}")
            print(f"     Violation : {check['violation']}")
            print(f"     CDISC Domain: {check['cdisc_domain']}")
            violations.append({"source": "snowflake", "table": check["table"], "detail": check["violation"]})
            log_event("GUARDIAN", "DATA_QUALITY_FAIL", check["violation"], check["severity"])
        elif check["status"] == "WARN":
            print(f"\n  ⚠️  DATA QUALITY WARN: {check['table']}")
            print(f"     {check['violation']}")

    print(f"\n  Total violations found: {len(violations)}")
    return violations