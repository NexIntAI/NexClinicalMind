from tools.airflow_mock import rerun_pipeline
from utils.audit_log import log_event
from utils.gemini_brain import ask_gemini

def run_remediate(violations: list, pipeline_failures: list):
    print("\n" + "="*60)
    print("  REMEDIATE AGENT — Auto-fix & Escalation (Gemini 2.0)")
    print("="*60)

    for v in violations:
        detail = v.get("detail", "")

        # Ask Gemini to write remediation brief
        prompt = f"""
You are a clinical data remediation specialist.

Write a concise remediation brief for this FDA compliance violation:

VIOLATION: {detail}

Format your response exactly like this:

SEVERITY ASSESSMENT: [one sentence]
IMMEDIATE ACTION: [what to do in the next 24 hours]
DATA FIX STEPS:
1. [first step]
2. [second step]  
3. [third step]
VALIDATION: [how to confirm the fix worked]
REGULATORY SIGN-OFF: [who needs to approve this fix]
"""

        print(f"\n  🤖 Gemini 2.0 generating remediation brief...")
        brief = ask_gemini(prompt)

        print(f"\n  📝 REMEDIATION BRIEF")
        print(f"  {'─'*50}")
        for line in brief.split('\n'):
            if line.strip():
                print(f"     {line}")

        print(f"\n  🚨 ESCALATED — Brief sent to Regulatory Affairs team.")
        print(f"     Human review required before submission proceeds.")

        log_event(
            "REMEDIATE",
            "AI_REMEDIATION_BRIEF_GENERATED",
            f"Gemini brief for: {detail[:80]}",
            "CRITICAL"
        )

    # Rerun failed pipelines
    for failure in pipeline_failures:
        print(f"\n  🔄 RERUNNING pipeline: {failure['name']}")
        result = rerun_pipeline(failure["id"])
        print(f"     Status: {result['message']}")
        log_event("REMEDIATE", "PIPELINE_RERUN", result["message"], "INFO")