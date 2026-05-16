import datetime
import json

def log_event(agent: str, action: str, detail: str, severity: str = "INFO"):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "agent": agent,
        "action": action,
        "detail": detail,
        "severity": severity,
        "standard": "21 CFR Part 11"
    }
    line = json.dumps(entry)
    print(f"\n[AUDIT LOG] {line}")
    with open("audit_trail.json", "a") as f:
        f.write(line + "\n")
    return entry