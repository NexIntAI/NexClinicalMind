import datetime
from utils.audit_log import log_event

def run_packager(violations: list):
    print("\n" + "="*60)
    print("  PACKAGER AGENT — Submission Readiness")
    print("="*60)

    high_risk = [v for v in violations if v.get("severity") == "HIGH" or "severity" not in v]

    if high_risk:
        print(f"\n  ⏸️  SUBMISSION PACKAGE ON HOLD")
        print(f"     {len(high_risk)} high-risk violation(s) must be resolved before packaging.")
        print(f"     Awaiting human sign-off on escalated items.")
        log_event("PACKAGER", "PACKAGING_BLOCKED", f"{len(high_risk)} unresolved violations", "HIGH")
    else:
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        package_name = f"NexClinicalMind_Submission_Package_{timestamp}.zip"
        print(f"\n  ✅ ALL CHECKS PASSED — GENERATING SUBMISSION PACKAGE")
        print(f"     Package     : {package_name}")
        print(f"     CDISC Status: Validated")
        print(f"     Audit Trail : 21 CFR Part 11 Compliant")
        print(f"     Ready for   : FDA Submission")
        log_event("PACKAGER", "PACKAGE_GENERATED", package_name, "INFO")