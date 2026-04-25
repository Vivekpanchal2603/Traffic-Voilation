from pathlib import Path
from app.services.yolo_engine import run_yolo_detection


UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

OUTPUT_DIR.mkdir(exist_ok=True)


def process_video(job_id: str):
    video_files = list(UPLOAD_DIR.glob(f"{job_id}.*"))

    if not video_files:
        return None

    video_path = video_files[0]

    output_folder = OUTPUT_DIR / job_id
    output_folder.mkdir(exist_ok=True)

    result = run_yolo_detection(
        video_path=str(video_path),
        output_folder=str(output_folder),
        weights_path="models/best.pt"  # change later if needed
    )

    return result