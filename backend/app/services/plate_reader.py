import re
import csv
import os
import base64
from pathlib import Path
from collections import Counter
from datetime import datetime
import uuid
import groq
from dotenv import load_dotenv

load_dotenv()

client = groq.Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

CSV_FILE = "violations.csv"
MAX_PLATE_IMAGES = 2


def clean_plate_text(text: str) -> str:
    text = text.strip().upper()
    return re.sub(r'[^A-Z0-9]', '', text)


def is_valid_plate_candidate(text: str) -> bool:
    return 8 <= len(text) <= 12


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(
            f.read()
        ).decode("utf-8")


def call_groq_vision(prompt: str, image_path: str) -> str:
    image_b64 = encode_image(image_path)

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content.strip()


def analyze_rider_violations(rider_crop_path: str) -> dict:
    prompt = """
Analyze this motorcycle rider image.

Return ONLY in this exact JSON format:
{
  "helmet_violation": true/false,
  "triple_seat_violation": true/false,
  "phone_violation": true/false
}

Rules:
- helmet_violation: true if any rider has no helmet.
- triple_seat_violation: true if 3 or more riders are on same bike.
- Count partially visible/overlapping riders.
- If 3 heads/bodies visible on one bike, triple_seat_violation = true.
- phone_violation: true only if driver is clearly using/holding phone.

Return JSON only.
"""

    raw = call_groq_vision(prompt, rider_crop_path)

    print("[VIOLATION AI RAW]", raw)

    try:
        helmet = (
            "helmet_violation" in raw and
            "true" in raw.split("helmet_violation")[1].split(",")[0].lower()
        )

        triple = (
            "triple_seat_violation" in raw and
            "true" in raw.split("triple_seat_violation")[1].split(",")[0].lower()
        )

        phone = (
            "phone_violation" in raw and
            "true" in raw.split("phone_violation")[1].split("}")[0].lower()
        )

        return {
            "helmet_violation": helmet,
            "triple_seat_violation": triple,
            "phone_violation": phone
        }

    except Exception:
        return {
            "helmet_violation": False,
            "triple_seat_violation": False,
            "phone_violation": False
        }


def get_best_plate_number(plates_folder: str) -> str:
    plates_path = Path(plates_folder)

    if not plates_path.exists():
        return ""

    plate_files = sorted(
        plates_path.glob("plate_best_*.jpg"),
        key=lambda p: int(p.stem.split("_")[-1])
    )[:MAX_PLATE_IMAGES]

    predictions = []

    prompt = """
Extract the Indian vehicle number plate text.
Return ONLY the plate text.
No explanation.
"""

    for plate_file in plate_files:
        raw = call_groq_vision(
            prompt,
            str(plate_file)
        )

        cleaned = clean_plate_text(raw)

        print("[PLATE RAW]", raw)

        if is_valid_plate_candidate(cleaned):
            predictions.append(cleaned)

    if not predictions:
        return ""

    best_plate, _ = Counter(predictions).most_common(1)[0]

    return best_plate


def calculate_fine(data: dict) -> int:
    fine = 0

    if data["helmet_violation"]:
        fine += 500

    if data["triple_seat_violation"]:
        fine += 500

    if data["phone_violation"]:
        fine += 500

    return fine


def save_violation_to_csv(data: dict):
    file_exists = Path(CSV_FILE).exists()

    fine_amount = calculate_fine(data)

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "violation_id",
                "timestamp",
                "number_plate",
                "helmet_violation",
                "triple_seat_violation",
                "phone_violation",
                "fine_amount"
            ])

        writer.writerow([
            str(uuid.uuid4()),
            datetime.now().isoformat(),
            data["number_plate"],
            data["helmet_violation"],
            data["triple_seat_violation"],
            data["phone_violation"],
            fine_amount
        ])


def analyze_violation(job_id: str) -> dict:
    rider_crop = f"outputs/{job_id}/full_frames/frame_best_5.jpg"
    plates_folder = f"outputs/{job_id}/plates"

    violations = analyze_rider_violations(rider_crop)

    if any(violations.values()):
        plate_number = get_best_plate_number(
            plates_folder
        )
    else:
        plate_number = ""

    fine_amount = calculate_fine({
        "number_plate": plate_number,
        **violations
    })

    final_result = {
        "number_plate": plate_number,
        **violations,
        "fine_amount": fine_amount
    }

    if any(violations.values()):
        save_violation_to_csv(final_result)

    return final_result