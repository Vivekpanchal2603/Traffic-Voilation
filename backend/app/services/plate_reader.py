import re
import base64
import requests
from pathlib import Path
from collections import Counter


OLLAMA_MODEL = "minicpm-v"

MAX_PLATE_IMAGES = 2   # reduced for speed
MAX_TRIPLE_IMAGES = 1  # only best frame


def clean_plate_text(text: str) -> str:
    text = text.strip().upper()
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text


def is_valid_plate_candidate(text: str) -> bool:
    return 8 <= len(text) <= 12


def call_ollama(prompt: str, image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        image_b64 = base64.b64encode(img_file.read()).decode("utf-8")

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False
    }

    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        timeout=320
    )

    data = response.json()

    return data.get("response", "").strip()


def get_best_plate_number(plates_folder: str) -> str:
    plates_path = Path(plates_folder)

    if not plates_path.exists():
        return ""

    plate_files = sorted(
        plates_path.glob("plate_best_*.jpg"),
        key=lambda p: int(p.stem.split("_")[-1])
    )[:MAX_PLATE_IMAGES]

    predictions = []

    prompt = (
        "Read Indian vehicle number plate. "
        "Return ONLY plate text in uppercase. "
        "No explanation."
    )

    for plate_file in plate_files:
        raw = call_ollama(prompt, str(plate_file))

        cleaned = clean_plate_text(raw)

        print("[PLATE RAW]", raw)

        if is_valid_plate_candidate(cleaned):
            predictions.append(cleaned)

    if not predictions:
        return ""

    best_plate, _ = Counter(predictions).most_common(1)[0]

    return best_plate


def detect_triple_seat(triple_crop_folder: str) -> bool:
    triple_path = Path(triple_crop_folder)

    if not triple_path.exists():
        return False

    crop_files = sorted(
        triple_path.glob("triple_crop_*.jpg"),
        key=lambda p: int(p.stem.split("_")[-1])
    )[:1]

    if not crop_files:
        return False

    prompt = """
Count ONLY the people riding on the motorcycle/scooter shown.

Rules:
- Ignore background people
- Ignore nearby vehicles
- Return ONLY the number: 1, 2, 3, or 4
"""

    raw = call_ollama(prompt, str(crop_files[0]))

    print("[TRIPLE RAW]", raw)

    match = re.search(r'\d+', raw)

    if match:
        return int(match.group()) >= 3

    return False


def analyze_violation(job_id: str) -> dict:
    plates_folder = f"outputs/{job_id}/plates"
    triple_crop_folder = f"outputs/{job_id}/triple_crop"

    plate_number = get_best_plate_number(plates_folder)

    triple_seat = False

    if plate_number:
        triple_seat = detect_triple_seat(triple_crop_folder)

    return {
        "plate_number": plate_number,
        "triple_seat": triple_seat
    }