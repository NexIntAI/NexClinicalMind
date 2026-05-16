from tools.airflow_mock import get_pipeline_status, rerun_pipeline
from utils.audit_log import log_event
from utils.gemini_brain import ask_gemini

def run_sentinel():
    print("\n" + "="*60)
    print("  SENTINEL AGENT — Pipeline Monitor (Gemini 2.0)")
    print("="*60)

    pipelines = get_pipeline_status()
    failures = [p for p in pipelines if p["status"] == "failed"]

    log_event(
        agent="SENTINEL",
        action="PIPELINE_SCAN",
        detail=f"Scanned {len(pipelines)} pipelines. Found {len(failures)} failure(s).",
        severity="INFO"
    )

    if failures:
        for f in failures:
            print(f"\n  ❌ FAILURE DETECTED: {f['name']}")
            print(f"     Pipeline ID : {f['id']}")
            print(f"     Error       : {f.get('error', 'Unknown')}")
            print(f"     Failed at   : {f.get('failed_at', 'Unknown')}")

            # Ask Gemini to diagnose root cause
            prompt = f"""
You are an expert clinical data pipeline engineer.

A pharmaceutical data pipeline has failed with this error:

PIPELINE NAME: {f['name']}
ERROR: {f.get('error', 'Unknown error')}
FAILED AT: {f.get('failed_at', 'Unknown')}

In 3 sentences maximum, explain:
1. The most likely root cause
2. The immediate impact on clinical trial data
3. The fastest fix

Be specific and technical. No bullet points — plain sentences only.
"""
            print(f"\n  🤖 Gemini 2.0 diagnosing root cause...")
            diagnosis = ask_gemini(prompt)
            print(f"\n  🔍 ROOT CAUSE ANALYSIS:")
            print(f"  {'─'*50}")
            for line in diagnosis.split('\n'):
                if line.strip():
                    print(f"     {line}")

            log_event(
                "SENTINEL",
                "FAILURE_DETECTED",
                f"Pipeline '{f['name']}' failed: {f.get('error')}",
                "CRITICAL"
            )
            log_event(
                "SENTINEL",
                "AI_DIAGNOSIS",
                diagnosis[:200],
                "INFO"
            )
    else:
        print("\n  ✅ All pipelines healthy.")

    return failures