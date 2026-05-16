import sys
import time
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

from agents.sentinel  import run_sentinel
from agents.guardian  import run_guardian
from agents.counsel   import run_counsel
from agents.remediate import run_remediate
from agents.packager  import run_packager

print("\n" + "★"*60)
print("  NexClinicalMind — Autonomous Clinical Trial Compliance Agent")
print("  Powered by Google ADK + Gemini 2.5 Flash + CrewAI + MCP")
print("★"*60)

print("\n🚀 Starting autonomous compliance scan...\n")
time.sleep(1)

# Agent 1: Detect pipeline failures
pipeline_failures = run_sentinel()
time.sleep(1)

# Agent 2: Validate CDISC compliance
violations = run_guardian()
time.sleep(1)

# Agent 3: Issue regulatory guidance
guidance = run_counsel(violations)
time.sleep(1)

# Agent 4: Remediate and escalate
run_remediate(violations, pipeline_failures)
time.sleep(1)

# Agent 5: Package or hold submission
run_packager(violations)

print("\n" + "★"*60)
print("  NexClinicalMind scan complete. Audit trail saved to audit_trail.json")
print("★"*60 + "\n")