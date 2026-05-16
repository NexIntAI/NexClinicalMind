# Controlled by api.py
SCAN_MODE = "violation"

def get_data_quality_results():
    if SCAN_MODE == "clean":
        return [
            {"table": "CLINICAL_TRIAL_EVENTS", "check": "CDISC_AETERM_NOT_NULL",
             "status": "PASS", "violation": None, "cdisc_domain": "AE", "severity": None},
            {"table": "PATIENT_DEMOGRAPHICS",  "check": "SUBJECT_ID_UNIQUE",
             "status": "PASS", "violation": None, "cdisc_domain": "DM", "severity": None},
            {"table": "LAB_RESULTS",           "check": "LBORRESU_VALID_UNIT",
             "status": "PASS", "violation": None, "cdisc_domain": "LB", "severity": None},
        ]
    if SCAN_MODE == "consent":
        return [
            {"table": "INFORMED_CONSENT", "check": "ICDTC_NOT_NULL",
             "status": "FAIL",
             "violation": "23 subjects missing ICDTC — required by FDA 21 CFR 50 and CDISC SDTM IC domain",
             "cdisc_domain": "IC", "severity": "HIGH"},
            {"table": "INFORMED_CONSENT", "check": "ICVERSION_VALID",
             "status": "FAIL",
             "violation": "8 subjects have outdated ICF version — consent must be re-obtained",
             "cdisc_domain": "IC", "severity": "HIGH"},
            {"table": "PATIENT_DEMOGRAPHICS", "check": "SUBJECT_ID_UNIQUE",
             "status": "PASS", "violation": None, "cdisc_domain": "DM", "severity": None},
            {"table": "LAB_RESULTS", "check": "LBORRESU_VALID_UNIT",
             "status": "WARN",
             "violation": "5 records with non-standard unit codes",
             "cdisc_domain": "LB", "severity": "LOW"},
        ]
    return [
        {"table": "CLINICAL_TRIAL_EVENTS", "check": "CDISC_AETERM_NOT_NULL",
         "status": "FAIL",
         "violation": "47 records missing AETERM (Adverse Event Term) — required by FDA CDISC SDTM",
         "cdisc_domain": "AE", "severity": "HIGH"},
        {"table": "PATIENT_DEMOGRAPHICS",  "check": "SUBJECT_ID_UNIQUE",
         "status": "PASS", "violation": None, "cdisc_domain": "DM", "severity": None},
        {"table": "LAB_RESULTS",           "check": "LBORRESU_VALID_UNIT",
         "status": "WARN",
         "violation": "12 records have non-standard unit codes — CDISC SDTM LB domain recommendation",
         "cdisc_domain": "LB", "severity": "LOW"},
    ]