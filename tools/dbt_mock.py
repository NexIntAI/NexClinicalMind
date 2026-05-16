# Controlled by api.py
SCAN_MODE = "violation"

def get_dbt_run_status():
    if SCAN_MODE == "clean":
        return [
            {"model": "stg_clinical_events",      "status": "success", "rows": 15420},
            {"model": "stg_patient_demographics",  "status": "success", "rows": 3201},
            {"model": "int_cdisc_sdtm_ae",         "status": "success", "rows": 8847},
            {"model": "mart_trial_summary",        "status": "success", "rows": 892},
        ]
    if SCAN_MODE == "consent":
        return [
            {"model": "stg_clinical_events",    "status": "success", "rows": 15420},
            {"model": "stg_informed_consent",   "status": "error",
             "error": "23 subjects missing ICDTC (Informed Consent Date) — violates CDISC SDTM IC domain requirement",
             "rows_affected": 23},
            {"model": "int_cdisc_sdtm_ae",      "status": "success", "rows": 8847},
            {"model": "mart_trial_summary",     "status": "skipped", "reason": "Upstream model stg_informed_consent failed"},
        ]
    return [
        {"model": "stg_clinical_events",      "status": "success", "rows": 15420},
        {"model": "stg_patient_demographics", "status": "success", "rows": 3201},
        {"model": "int_cdisc_sdtm_ae",        "status": "error",
         "error": "Column 'AETERM' contains NULL values — violates CDISC SDTM AE domain requirement",
         "rows_affected": 47},
        {"model": "mart_trial_summary",       "status": "skipped", "reason": "Upstream failure"},
    ]