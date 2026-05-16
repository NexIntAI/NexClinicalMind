from utils.audit_log import log_event
from utils.gemini_brain import ask_gemini

def run_counsel(violations: list):
    print("\n" + "="*60)
    print("  COUNSEL AGENT — Regulatory Intelligence (Gemini 2.0)")
    print("="*60)

    guidance_issued = []

    for v in violations:
        detail = v.get("detail", "")

        # Build prompt for Gemini
        prompt = f"""
You are an expert FDA regulatory affairs specialist with deep knowledge of:
- FDA 21 CFR Part 11 (Electronic Records and Signatures)
- CDISC SDTM v3.3 standards
- ICH E6 Good Clinical Practice guidelines
- FDA drug submission requirements

A clinical trial data compliance violation has been detected:

VIOLATION: {detail}
SOURCE: {v.get('source', 'unknown')} 
CDISC DOMAIN: {v.get('cdisc_domain', v.get('model', 'unknown'))}

Provide a concise regulatory response in exactly this format:

REGULATION: [exact regulation name and section]
REQUIREMENT: [what the regulation requires in one sentence]
RISK: [HIGH/MEDIUM/LOW] — [why this is a risk for FDA submission]
REMEDIATION: [specific step-by-step fix in 2-3 sentences]
URGENCY: [how quickly this must be fixed before it blocks submission]
"""

        print(f"\n  🤖 Consulting Gemini 2.0 Flash for: {detail[:60]}...")
        response = ask_gemini(prompt)

        print(f"\n  📋 REGULATORY GUIDANCE (AI-Generated)")
        print(f"  {'─'*50}")
        # Print each line with indentation
        for line in response.split('\n'):
            if line.strip():
                print(f"     {line}")

        log_event(
            "COUNSEL",
            "AI_REGULATORY_GUIDANCE_ISSUED",
            f"Gemini 2.0 guidance for: {detail[:80]}",
            "INFO"
        )

        guidance_issued.append({
            "violation": detail,
            "guidance": response
        })

    return guidance_issued