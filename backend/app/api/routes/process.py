from fastapi import APIRouter, HTTPException

from app.services.detector import process_video
from app.services.plate_reader import analyze_violation
from app.services.email_service import send_challan_email

router = APIRouter()


@router.post("/process/{job_id}")
def process_uploaded_video(
    job_id: str,
    auto_email: bool = True
):
    result = process_video(job_id)

    if not result:
        raise HTTPException(status_code=404, detail="Video not found")

    ai_result = analyze_violation(job_id)

    result.update(ai_result)

    result["violation_detected"] = any([
        ai_result["helmet_violation"],
        ai_result["triple_seat_violation"],
        ai_result["phone_violation"]
    ])

    # SEND EMAIL ONLY IF VIOLATION EXISTS
    if result["violation_detected"] and auto_email:

        send_challan_email(
            plate_no=ai_result["number_plate"],
            fine_amount=ai_result["fine_amount"],
            helmet_violation=ai_result["helmet_violation"],
            triple_seat_violation=ai_result["triple_seat_violation"],
            phone_violation=ai_result["phone_violation"],

            plate_img_path=f"outputs/{job_id}/plates/plate_best_1.jpg",

            full_img_path=f"outputs/{job_id}/full_frames/frame_best_1.jpg"
        )

    return {
        "success": True,
        "job_id": job_id,
        "result": result
    }