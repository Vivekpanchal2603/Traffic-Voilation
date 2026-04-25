from fastapi import APIRouter, HTTPException

from app.services.detector import process_video
from app.services.plate_reader import analyze_violation

router = APIRouter()


@router.post("/process/{job_id}")
def process_uploaded_video(job_id: str):
    result = process_video(job_id)

    if not result:
        raise HTTPException(status_code=404, detail="Video not found")

    ai_result = analyze_violation(job_id)

    result["plate_number"] = ai_result["plate_number"]
    result["triple_seat"] = ai_result["triple_seat"]

    if ai_result["triple_seat"]:
        result["violation_detected"] = True

    return {
        "success": True,
        "job_id": job_id,
        "result": result
    }