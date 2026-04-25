import uuid
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def save_upload(file):
    job_id = str(uuid.uuid4())

    extension = file.filename.split(".")[-1]
    filename = f"{job_id}.{extension}"

    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return job_id, str(file_path)