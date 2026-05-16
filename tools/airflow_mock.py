import random

PIPELINES = [
    {"id": "pipeline_clinical_trial_001", "name": "Phase III Trial Data Ingestion", "status": "running"},
    {"id": "pipeline_lab_results_002",    "name": "Lab Results Processing",         "status": "running"},
    {"id": "pipeline_patient_records_003","name": "Patient Records Sync",           "status": "running"},
    {"id": "pipeline_cdisc_mapping_004",  "name": "CDISC SDTM Mapping",            "status": "running"},
]

# Controlled by API — default is violation mode
SCAN_MODE = "violation"

def get_pipeline_status():
    pipelines = [p.copy() for p in PIPELINES]
    if SCAN_MODE == "violation":
        failed_index = random.randint(0, len(pipelines) - 1)
        pipelines[failed_index]["status"] = "failed"
        pipelines[failed_index]["error"] = "Schema mismatch detected in source EHR system"
        pipelines[failed_index]["failed_at"] = "2026-05-10T14:32:11Z"
    elif SCAN_MODE == "consent":
        pipelines[2]["status"] = "failed"
        pipelines[2]["error"] = "Informed consent records missing for 23 trial subjects in ICF domain"
        pipelines[2]["failed_at"] = "2026-05-10T09:15:44Z"
    return pipelines

def rerun_pipeline(pipeline_id: str):
    return {
        "pipeline_id": pipeline_id,
        "action": "rerun_triggered",
        "status": "queued",
        "message": f"Pipeline {pipeline_id} successfully queued for rerun"
    }