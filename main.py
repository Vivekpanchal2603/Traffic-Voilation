import cv2
from pathlib import Path
from ultralytics import YOLO
import numpy as np
import os
import datetime


# ---------------- CONFIG ----------------
CLASS_NAMES = ['number plate', 'no helmet', 'helmet', 'helmet', 'bike']
CONF_THRESH = 0.30

COLOR_DICT = {
    "helmet": (0, 255, 0),
    "no helmet": (0, 0, 255),
    "number plate": (255, 255, 0),
    "bike": (255, 255, 255)
}

PHONE_WIDTH = 480
PHONE_HEIGHT = 720

TOP_PLATE_COUNT = 25
TOP_HELMET_COUNT = 10
TOP_FULL_COUNT = 10


def xyxy_to_int(box):
    return [int(x) for x in box]


def create_attractive_summary(helmet_text, triple_text, avg_helmet, avg_nohelmet, abs_persons):
    """Create an attractive final summary display"""
    # Create background with gradient
    final_img = 255 * np.ones((PHONE_HEIGHT, PHONE_WIDTH, 3), dtype=np.uint8)
    
    # Add gradient background
    for i in range(PHONE_HEIGHT):
        alpha = i / PHONE_HEIGHT
        final_img[i, :, :] = final_img[i, :, :] * (1 - alpha) + np.array([240, 240, 245]) * alpha

    # Add header with background
    header_height = 100
    cv2.rectangle(final_img, (0, 0), (PHONE_WIDTH, header_height), (25, 25, 112), -1)
    
    # Main title with shadow effect
    cv2.putText(final_img, "FINAL VIOLATION REPORT", (45, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 3)
    cv2.putText(final_img, "FINAL VIOLATION REPORT", (40, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 3)

    # Add decorative line
    cv2.line(final_img, (40, 80), (PHONE_WIDTH - 40, 80), (70, 130, 180), 2)

    y_offset = 180

    # Helmet status with icon and box
    helmet_has_violation = "No Helmet" in helmet_text
    color_helmet = (0, 0, 255) if helmet_has_violation else (0, 180, 0)
    bg_color_helmet = (0, 0, 100) if helmet_has_violation else (0, 100, 0)
    
    # Background box for helmet status
    cv2.rectangle(final_img, (30, y_offset - 50), (PHONE_WIDTH - 30, y_offset + 10), bg_color_helmet, -1)
    cv2.rectangle(final_img, (30, y_offset - 50), (PHONE_WIDTH - 30, y_offset + 10), color_helmet, 2)
    
    # Helmet icon (simple circle)
    cv2.circle(final_img, (60, y_offset - 20), 15, color_helmet, -1)
    cv2.putText(final_img, "Helmet Status:", (90, y_offset - 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(final_img, helmet_text, (90, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Confidence scores for helmet
    conf_text = f"Helmet: {avg_helmet:.2f} | No-Helmet: {avg_nohelmet:.2f}"
    cv2.putText(final_img, conf_text, (90, y_offset + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    # Triple riding status with icon and box
    triple_has_violation = "More than 2" in triple_text
    color_triple = (0, 0, 255) if triple_has_violation else (0, 180, 0)
    bg_color_triple = (0, 0, 100) if triple_has_violation else (0, 100, 0)

    # Background box for triple riding status
    cv2.rectangle(final_img, (30, y_offset + 40), (PHONE_WIDTH - 30, y_offset + 100), bg_color_triple, -1)
    cv2.rectangle(final_img, (30, y_offset + 40), (PHONE_WIDTH - 30, y_offset + 100), color_triple, 2)
    
    # Triple riding icon (three circles)
    cv2.circle(final_img, (50, y_offset + 70), 8, color_triple, -1)
    cv2.circle(final_img, (65, y_offset + 70), 8, color_triple, -1)
    cv2.circle(final_img, (80, y_offset + 70), 8, color_triple, -1)
    
    cv2.putText(final_img, "Riding Status:", (100, y_offset + 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(final_img, triple_text, (100, y_offset + 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Rider count info
    count_text = f"Avg Riders: {abs_persons}"
    cv2.putText(final_img, count_text, (100, y_offset + 115),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)




    # Add timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(final_img, f"Generated: {timestamp}", (40, PHONE_HEIGHT - 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)

    # Add footer
    cv2.putText(final_img, "AI Traffic Monitoring System", (PHONE_WIDTH//2 - 150, PHONE_HEIGHT - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

    return final_img


def run(video_source, weights_path):
    print(" Loading YOLOv8 model...")
    model = YOLO(weights_path)

    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        raise ValueError(f" Could not open video: {video_source}")

    video_name = Path(video_source).stem
    OUTPUT_DIR = Path("outputs") / video_name

    PLATES_DIR = OUTPUT_DIR / "plates"
    HELMETS_DIR = OUTPUT_DIR / "helmets"
    FULL_DIR = OUTPUT_DIR / "full_frames"

    folders_created = False
    frame_idx = 0
    pause_done = False

    helmet_conf_list = []
    nohelmet_conf_list = []
    frame_person_counts = []

    top_helmet = []
    top_plate = []
    top_full = []

    while True:
        ret, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180) 
        if not ret:
            break
        frame_idx += 1

        results = model.predict(frame, conf=CONF_THRESH, verbose=False)
        boxes = results[0].boxes
        violation_detected_this_frame = False
        frame_rider_count = 0

        if boxes is not None and len(boxes) > 0:
            for box, cls_id, conf in zip(boxes.xyxy, boxes.cls, boxes.conf):
                cls_idx = int(cls_id)
                if cls_idx >= len(CLASS_NAMES):
                    continue

                raw_name = CLASS_NAMES[cls_idx]
                cls_name = "helmet" if raw_name == "helmet" else raw_name

                x1, y1, x2, y2 = xyxy_to_int(box.cpu().numpy())
                color = COLOR_DICT.get(cls_name, (255, 255, 255))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, cls_name, (x1, y1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                if cls_name == "helmet":
                    helmet_conf_list.append(float(conf))
                    frame_rider_count += 1

                elif cls_name == "no helmet":
                    nohelmet_conf_list.append(float(conf))
                    frame_rider_count += 1
                    violation_detected_this_frame = True

                    #  Create folders only when needed
                    if not folders_created:
                        PLATES_DIR.mkdir(parents=True, exist_ok=True)
                        HELMETS_DIR.mkdir(parents=True, exist_ok=True)
                        FULL_DIR.mkdir(parents=True, exist_ok=True)
                        folders_created = True

                    # Save top helmets
                    if len(top_helmet) < TOP_HELMET_COUNT:
                        top_helmet.append((float(conf), frame[y1:y2, x1:x2].copy()))
                    else:
                        min_idx = np.argmin([c for c, _ in top_helmet])
                        if float(conf) > top_helmet[min_idx][0]:
                            top_helmet[min_idx] = (float(conf), frame[y1:y2, x1:x2].copy())

                elif cls_name == "number plate":
                    plate_crop = frame[y1:y2, x1:x2].copy()
                    h, w = plate_crop.shape[:2]
                    if h < 25 or w < 70:
                        continue
                    if len(top_plate) < TOP_PLATE_COUNT:
                        top_plate.append((float(conf), plate_crop))
                    else:
                        min_idx = np.argmin([c for c, _ in top_plate])
                        if float(conf) > top_plate[min_idx][0]:
                            top_plate[min_idx] = (float(conf), plate_crop)

        frame_person_counts.append(frame_rider_count)

        # --- Pause once when a violation detected ---
        if violation_detected_this_frame and not pause_done:
            print(f"[{frame_idx}]  No helmet detected - Pausing")
            cv2.imshow("Helmet+Plate Detection", cv2.resize(frame, (PHONE_WIDTH, PHONE_HEIGHT)))
            cv2.waitKey(5000)
            pause_done = True

        # Top full frames
        if violation_detected_this_frame:
            if len(top_full) < TOP_FULL_COUNT:
                top_full.append((frame_idx, frame.copy()))
            else:
                min_idx = np.argmin([idx for idx, _ in top_full])
                top_full[min_idx] = (frame_idx, frame.copy())

        frame_resized = cv2.resize(frame, (PHONE_WIDTH, PHONE_HEIGHT))
        key = cv2.waitKey(1)
        cv2.imshow("Helmet+Plate Detection", frame_resized)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    # ---------------- FINAL RESULT ----------------
    avg_helmet = np.mean(helmet_conf_list) if helmet_conf_list else 0
    avg_nohelmet = np.mean(nohelmet_conf_list) if nohelmet_conf_list else 0
    avg_persons = np.mean(frame_person_counts) if frame_person_counts else 0
    abs_persons = int(round(avg_persons))

    violation = False
    helmet_text = ""
    triple_text = ""

    if avg_nohelmet > avg_helmet:
        violation = True
        helmet_text = "No Helmet Detected"
    else:
        helmet_text = "Helmet Worn Properly"

    if abs_persons > 2:
        violation = True
        triple_text = "More than 2 Riders"
    else:
        triple_text = "No Triple Seat Violation"

    print("\nFinal Result:")
    print(f"Avg helmet conf: {avg_helmet:.2f}, Avg no-helmet conf: {avg_nohelmet:.2f}")
    print(f"{helmet_text}")
    print(f"{triple_text}")

    #  Save if any violation (no helmet OR triple seat)
    if violation:
        if not folders_created:
            PLATES_DIR.mkdir(parents=True, exist_ok=True)
            HELMETS_DIR.mkdir(parents=True, exist_ok=True)
            FULL_DIR.mkdir(parents=True, exist_ok=True)

        for i, (_, img) in enumerate(top_helmet):
            cv2.imwrite(str(HELMETS_DIR / f"nohelmet_best_{i+1}.jpg"), img)
        for i, (_, img) in enumerate(top_plate):
            cv2.imwrite(str(PLATES_DIR / f"plate_best_{i+1}.jpg"), img)
        for i, (_, img) in enumerate(top_full):
            cv2.imwrite(str(FULL_DIR / f"full_best_{i+1}.jpg"), img)
        print(f" Saved violation images to {OUTPUT_DIR}/")
    else:
        print(" No violations detected — nothing saved.")

    # --- Display attractive final summary image ---
    final_img = create_attractive_summary(helmet_text, triple_text, avg_helmet, avg_nohelmet, abs_persons)
    cv2.imshow("FINAL RESULT", final_img)
    cv2.waitKey(5000)

    # ---------------- SAVE VIOLATION TYPE ----------------
    try:
        violation_list = []
        if avg_nohelmet > avg_helmet:
            violation_list.append("No Helmet")
        if abs_persons > 2:
            violation_list.append("Triple Seat")

        violation_type = " + ".join(violation_list) if violation_list else "No Violation"

        # Save in same folder as outputs
        violation_file = OUTPUT_DIR / "violation.txt"
        with open(violation_file, "w") as f:
            f.write(violation_type)

        print(f" Violation info saved to {violation_file}: {violation_type}")
    except Exception as e:
        print(" Could not save violation type:", e)

    # ---------------- RUN OCR & CHALLAN ----------------
    if violation:
        print("\n Running OCR and Challan System...")
        try:
            import subprocess
            import sys

            ocr_script = r"C:\Users\Vivek\Desktop\project\ocr.py"

            #  Pass the output folder dynamically to OCR
            subprocess.run(
                [sys.executable, ocr_script, "--output_dir", str(OUTPUT_DIR)],
                check=True
            )

        except Exception as e:
            print(" Error while running OCR:", e)
    else:
        print(" No violations detected — OCR not executed.")

    cv2.destroyAllWindows()


# ---------------- RUN ----------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, required=True)
    parser.add_argument("--weights", type=str, required=True)
    args = parser.parse_args()
    run(args.source, args.weights)