from fastapi import APIRouter, UploadFile, File
from app.services.storage import save_upload

router = APIRouter()

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    job_id, file_path = await save_upload(file)

    return {
        "success": True,
        "job_id": job_id,
        "filename": file.filename,
        "saved_path": file_path
    }