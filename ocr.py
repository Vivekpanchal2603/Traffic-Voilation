# import os
# import cv2
# import pandas as pd
# import easyocr
# import random
# from pathlib import Path
# import string
# import smtplib
# import geocoder
# from collections import Counter
# from datetime import datetime
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders

# # ---------------- CONFIG ----------------
# READS_PER_IMAGE = 5
# DATABASE_FILE = "challan_database.csv"
# CHALLAN_INCREMENT = 500

# # --------------- DATABASE ---------------
# def load_database():
#     if os.path.exists(DATABASE_FILE):
#         return pd.read_csv(DATABASE_FILE)
#     else:
#         return pd.DataFrame(columns=["Number Plate", "Name", "Surname", "Phone", "Challan", "Violation Type"])

# def save_database(df):
#     df.to_csv(DATABASE_FILE, index=False)

# def generate_dummy_info(existing_names):
#     first_names = ["Amit", "Rahul", "Vivek", "Neha", "Pooja", "Suresh", "Karan", "Rina"]
#     last_names = ["Sharma", "Verma", "Patel", "Gupta", "Yadav", "Rao", "Singh", "Mehta"]
#     while True:
#         name = random.choice(first_names)
#         surname = random.choice(last_names)
#         phone = "".join(random.choices(string.digits, k=10))
#         key = f"{name}_{surname}_{phone}"
#         if key not in existing_names:
#             return name, surname, phone

# # --------------- OCR FUNCTIONS ---------------
# def ocr_once(reader, img):
#     results = reader.readtext(img)
#     for (bbox, text, conf) in results:
#         if len(text) >= 6 and any(ch.isdigit() for ch in text):  # valid plate check
#             clean = "".join(ch for ch in text if ch.isalnum()).upper()
#             return clean
#     return None

# def merge_with_locking(all_candidates):
#     counter = Counter(all_candidates)
#     best = counter.most_common(1)[0][0]
#     return best

# # --------------- EMAIL FUNCTION ---------------
# def send_challan_email(name, surname, phone, plate_no, challan, plate_img_path, full_img_path, violation_type):
#     sender_email = "naughty.vivek26@gmail.com"
#     sender_pass = "irsemgsyacxnpdoe"  # <-- add app password here
#     receiver_email = "panchalvivek2603@gmail.com"

#     subject = f"🚨 Traffic Violation - {violation_type} for {plate_no}"
#     g = geocoder.ip('me')
#     location = g.city if g.ok else "Unknown Location"
#     time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     body = f"""
#     Dear {name} {surname},

#     A traffic violation has been recorded for your vehicle.

#     📸 Vehicle Number: {plate_no}
#     ⚠️ Violation Type: {violation_type}
#     💰 Challan Amount: ₹{challan}
#     📅 Date & Time: {time_now}
#     📍 Location: {location}
#     📞 Contact: {phone}

#     Please clear the challan at your nearest RTO office or online portal.

#     Regards,
#     Traffic Department Automated System
#     """

#     msg = MIMEMultipart()
#     msg["From"] = sender_email
#     msg["To"] = receiver_email
#     msg["Subject"] = subject
#     msg.attach(MIMEText(body, "plain"))

#     for path in [plate_img_path, full_img_path]:
#         if os.path.exists(path):
#             with open(path, "rb") as f:
#                 part = MIMEBase("application", "octet-stream")
#                 part.set_payload(f.read())
#                 encoders.encode_base64(part)
#                 part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
#                 msg.attach(part)

#     try:
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login(sender_email, sender_pass)
#             server.send_message(msg)
#             print(f" Email sent successfully for {plate_no}")
#     except Exception as e:
#         print(" Email sending failed:", e)

# # --------------- UPDATE CHALLAN FUNCTION ---------------
# def update_challan(final_plate, violation_type, output_folder):
#     df = load_database()
#     existing_names = set(df["Name"].astype(str) + "_" + df["Surname"].astype(str) + "_" + df["Phone"].astype(str))

#     if final_plate in df["Number Plate"].values:
#         df.loc[df["Number Plate"] == final_plate, "Challan"] += CHALLAN_INCREMENT
#         df.loc[df["Number Plate"] == final_plate, "Violation Type"] = violation_type
#         print(f" Existing plate found — ₹{CHALLAN_INCREMENT} added! Total challan updated.")
#     else:
#         name, surname, phone = generate_dummy_info(existing_names)
#         new_entry = {
#             "Number Plate": final_plate,
#             "Name": name,
#             "Surname": surname,
#             "Phone": phone,
#             "Challan": 500,
#             "Violation Type": violation_type
#         }
#         df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
#         print(f" New record added for {final_plate} — ₹500 challan issued ({violation_type}).")

#     save_database(df)
#     print(f" Database updated ({len(df)} total records)\n")

#     try:
#         record = df[df["Number Plate"] == final_plate].iloc[-1]
#         plate_img = str(output_folder / "plates" / "plate_best_20.jpg")
#         full_img = str(output_folder / "full_frames" / "full_best_10.jpg")

#         send_challan_email(
#             record["Name"], record["Surname"], record["Phone"],
#             record["Number Plate"], record["Challan"],
#             plate_img, full_img, violation_type
#         )
#     except Exception as e:
#         print(" Error while sending challan email:", e)

# # --------------- MAIN OCR PIPELINE ---------------
# def main(output_dir=None):
#     outputs_dir = Path("outputs")
#     if not outputs_dir.exists():
#         print(" No outputs folder found!")
#         return

#     #  If specific output folder provided
#     if output_dir:
#         target_folder = Path(output_dir)
#         if not target_folder.exists():
#             print(f" Provided output folder not found: {output_dir}")
#             return
#         latest_folder = target_folder
#     else:
#         latest_folder = max(outputs_dir.glob("*"), key=os.path.getctime)

#     PLATES_DIR = latest_folder / "plates"

#     # Read violation type
#     violation_file = latest_folder / "violation.txt"
#     violation_type = "Unknown Violation"
#     if violation_file.exists():
#         with open(violation_file, "r") as f:
#             violation_type = f.read().strip()

#     reader = easyocr.Reader(['en'], gpu=False)
#     all_candidates = []

#     images = [f for f in os.listdir(PLATES_DIR)
#               if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
#     print(f" Found {len(images)} plate images in {PLATES_DIR}\n")

#     for idx, fname in enumerate(images, 1):
#         path = os.path.join(PLATES_DIR, fname)
#         img = cv2.imread(path)
#         if img is None:
#             print(f"[{idx}] Skipping unreadable file: {fname}")
#             continue

#         results = []
#         for _ in range(READS_PER_IMAGE):
#             plate = ocr_once(reader, img)
#             if plate:
#                 results.append(plate)

#         if results:
#             best = Counter(results).most_common(1)[0][0]
#             all_candidates.append(best)
#             print(f"[{idx}]  Plate detected: {best}")
#         else:
#             print(f"[{idx}]  No plate detected in {fname}")

#     if not all_candidates:
#         print("\n No number plate detected in entire folder.")
#         return

#     final_plate = merge_with_locking(all_candidates)

#     print("\n---------------------------------------")
#     print(" Detected candidates:")
#     for c in all_candidates:
#         print("   ", c)
#     print("---------------------------------------")
#     print(f" FINAL VERIFIED NUMBER PLATE: {final_plate}")
#     print("---------------------------------------")

#     # Update and email challan
#     update_challan(final_plate, violation_type, latest_folder)

#     #  Auto-generate dashboard
#     try:
#         import dashboard_generator
#         dashboard_generator.generate_dashboard()
#     except Exception as e:
#         print(" Could not update dashboard:", e)


# # ---------------- RUN ----------------
# if __name__ == "__main__":
#     import argparse
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--output_dir", type=str, help="Path to the specific output folder from main.py")
#     args = parser.parse_args()
#     main(args.output_dir)



#best working for all nums shown in review






















# #!/usr/bin/env python3
# """
# ocr.py
# Complete OCR + correction + challan + email + dashboard runner.

# - Uses EasyOCR (CPU) with heavy preprocessing + multi-read + voting.
# - Indian plate auto-correction engine to fix remaining chars.
# - Updates a CSV database and optionally sends emails (via env vars).
# - Calls dashboard_generator.generate_dashboard() if available.
# """

# import os
# import cv2
# import pandas as pd
# import easyocr
# import random
# from pathlib import Path
# import string
# import smtplib
# import geocoder
# import numpy as np
# import re
# from collections import Counter
# from datetime import datetime
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders

# # ---------------- CONFIG ----------------
# READS_PER_IMAGE = 5
# DATABASE_FILE = "challan_database.csv"
# CHALLAN_INCREMENT = 500
# MAX_PLATE_LEN = 12

# # Valid Indian state codes for correction
# VALID_STATES = [
#     "AP","AR","AS","BR","CG","CH","DD","DL","DN","GA","GJ","HP","HR",
#     "JH","JK","KA","KL","LD","MH","MN","MP","MZ","NL","OD","PB","RJ",
#     "SK","TN","TS","UK","UP","WB"
# ]

# # allowed chars and swap dictionaries
# ALLOWED = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
# SWAPS = {'O':'0','D':'0','I':'1','L':'1','Z':'2','S':'5','B':'8','G':'6'}
# REV_SWAPS = {'5':'S','2':'Z','8':'B','1':'I','0':'O','6':'G'}

# # Initialize EasyOCR reader (CPU)
# READER = easyocr.Reader(['en'], gpu=False)

# # ---------------- DATABASE / UTILS ----------------
# def load_database():
#     if os.path.exists(DATABASE_FILE):
#         return pd.read_csv(DATABASE_FILE)
#     else:
#         return pd.DataFrame(columns=["Number Plate", "Name", "Surname", "Phone", "Challan", "Violation Type"])

# def save_database(df):
#     df.to_csv(DATABASE_FILE, index=False)

# def generate_dummy_info(existing_names):
#     first = ["Amit", "Rahul", "Vivek", "Neha", "Pooja", "Suresh", "Karan", "Rina"]
#     last = ["Sharma", "Verma", "Patel", "Gupta", "Yadav", "Rao", "Singh", "Mehta"]
#     while True:
#         n, s = random.choice(first), random.choice(last)
#         p = "".join(random.choices(string.digits, k=10))
#         key = f"{n}_{s}_{p}"
#         if key not in existing_names:
#             return n, s, p

# # ---------------- IMAGE PREPROCESSING ----------------
# def crop_tight(img, pad=0.12):
#     """Crop inner region to remove border noise"""
#     h, w = img.shape[:2]
#     y1 = int(h * pad); y2 = int(h * (1 - pad))
#     x1 = int(w * pad); x2 = int(w * (1 - pad))
#     # safety clamp
#     y1 = max(0, y1); x1 = max(0, x1)
#     y2 = min(h, y2); x2 = min(w, x2)
#     return img[y1:y2, x1:x2]

# def preprocess_for_ocr(img, upscale=2):
#     """
#     Preprocesses the plate crop:
#     - tight crop
#     - convert to gray
#     - upscale
#     - CLAHE
#     - unsharp/sharpen
#     """
#     if img is None:
#         return None
#     img = crop_tight(img, pad=0.12)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     gray = cv2.resize(gray, None, fx=upscale, fy=upscale, interpolation=cv2.INTER_CUBIC)
#     clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
#     gray = clahe.apply(gray)
#     blur = cv2.GaussianBlur(gray, (3,3), 0)
#     sharp = cv2.addWeighted(gray, 1.7, blur, -0.7, 0)
#     # small morphological open to remove specks
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
#     denoised = cv2.morphologyEx(sharp, cv2.MORPH_OPEN, kernel)
#     return denoised

# # ---------------- TEXT CLEANING & VOTING ----------------
# def clean_text_raw(text):
#     """Uppercase, remove non-alnum, apply swaps, whitelist"""
#     if not text:
#         return ""
#     text = str(text).upper()
#     text = "".join(ch for ch in text if ch.isalnum())
#     for k, v in SWAPS.items():
#         text = text.replace(k, v)
#     text = "".join(ch for ch in text if ch in ALLOWED)
#     return text[:MAX_PLATE_LEN]

# def per_char_vote(candidates):
#     """Right-aligned per-character voting to produce a robust plate string."""
#     if not candidates:
#         return ""
#     cleaned = [clean_text_raw(c) for c in candidates if c]
#     cleaned = [c for c in cleaned if len(c) >= 3]
#     if not cleaned:
#         return ""
#     max_len = max(len(c) for c in cleaned)
#     matrix = [c.rjust(max_len) for c in cleaned]
#     result_chars = []
#     for i in range(max_len):
#         chars = [row[i] for row in matrix if row[i] != ' ']
#         if chars:
#             most_common = Counter(chars).most_common(1)[0][0]
#             result_chars.append(most_common)
#     res = "".join(result_chars)
#     return clean_text_raw(res)

# def merge_with_locking(all_candidates):
#     """Prefer majority full-string, fallback to per-character voting."""
#     if not all_candidates:
#         return ""
#     counter = Counter(all_candidates)
#     most_common, cnt = counter.most_common(1)[0]
#     if cnt > 1:
#         return most_common
#     return per_char_vote(all_candidates)

# # ---------------- INDIAN PLATE AUTO-CORRECTION ----------------
# def fix_plate_format(plate):
#     """Apply Indian-format heuristics to correct state, rto, series, and last digits."""
#     plate = clean_text_raw(plate)
#     if len(plate) < 4:
#         return plate

#     # 1) Fix state (first two letters) by minimal char diffs
#     raw_state = plate[:2]
#     best_state = min(VALID_STATES, key=lambda s: sum(a!=b for a,b in zip(s, raw_state)))
#     plate = best_state + plate[2:]

#     # 2) Extract RTO code (1-2 digits)
#     rest = plate[2:]
#     rto = ""
#     for ch in rest:
#         if ch.isdigit():
#             rto += ch
#         else:
#             rto += SWAPS.get(ch, ch)
#         if len(rto) == 2:
#             break

#     # 3) Extract series (1-3 letters)
#     idx = 2 + len(rto)
#     series = ""
#     while idx < len(plate) and len(series) < 3:
#         ch = plate[idx]
#         if ch.isalpha():
#             series += ch
#         else:
#             series += REV_SWAPS.get(ch, ch)
#         idx += 1

#     # 4) Extract trailing numbers (1-4 digits)
#     last = ""
#     while idx < len(plate) and len(last) < 4:
#         ch = plate[idx]
#         if ch.isdigit():
#             last += ch
#         else:
#             last += SWAPS.get(ch, ch)
#         idx += 1

#     final = (best_state + rto + series + last)[:MAX_PLATE_LEN]
#     return final

# # ---------------- OCR READ (multi-read) ----------------
# def ocr_multi_read(img, reader, reads=READS_PER_IMAGE):
#     """
#     Multi-read on slightly varying preprocessed images to gather candidates,
#     then aggregate via merge_with_locking and correct via fix_plate_format.
#     """
#     if img is None:
#         return None
#     candidates = []
#     for i in range(reads):
#         prep = preprocess_for_ocr(img, upscale=2)
#         if prep is None:
#             continue

#         # vary input: sometimes use adaptive threshold for diversity
#         if i % 2 == 0:
#             proc_img = prep
#         else:
#             proc_img = cv2.adaptiveThreshold(prep, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                              cv2.THRESH_BINARY, 11, 2)

#         try:
#             res = reader.readtext(proc_img, detail=1, paragraph=False)
#         except Exception as e:
#             res = []

#         texts = []
#         for bbox, text, conf in res:
#             txt = "".join(ch for ch in text if ch.isalnum())
#             if len(txt) >= 3 and any(ch.isdigit() for ch in txt):
#                 texts.append(txt)

#         if texts:
#             joined = "".join(texts)
#             candidates.append(clean_text_raw(joined))

#     if not candidates:
#         return None

#     merged = merge_with_locking(candidates)
#     final = fix_plate_format(merged)
#     if len(final) < 5:
#         return None
#     return final

# # ---------------- EMAIL FUNCTION ----------------
# def send_challan_email(name, surname, phone, plate_no, challan, plate_img_path, full_img_path, violation_type):
#     """
#     Send email if SMTP env vars present:
#     - SMTP_FROM
#     - SMTP_PASS (Gmail app password)
#     - SMTP_TO
#     If SMTP_PASS is missing, email is skipped.
#     """
#     sender_email = os.getenv("SMTP_FROM", "")
#     sender_pass = os.getenv("SMTP_PASS", "")
#     receiver_email = os.getenv("SMTP_TO", "panchalvivek2603@gmail.com")

#     if not sender_pass or not sender_email:
#         print("⚠️ SMTP credentials not provided. Email skipped.")
#         return

#     subject = f"🚨 Traffic Violation - {violation_type} for {plate_no}"
#     try:
#         g = geocoder.ip('me')
#         location = g.city if g.ok else "Unknown"
#     except Exception:
#         location = "Unknown"

#     time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     body = f"""
# Dear {name} {surname},

# A traffic violation has been recorded for your vehicle.

# 📸 Vehicle Number: {plate_no}
# ⚠️ Violation Type: {violation_type}
# 💰 Challan Amount: ₹{challan}
# 📅 Date & Time: {time_now}
# 📍 Location: {location}
# 📞 Contact: {phone}

# Regards,
# Traffic Department Automated System
# """

#     msg = MIMEMultipart()
#     msg["From"], msg["To"], msg["Subject"] = sender_email, receiver_email, subject
#     msg.attach(MIMEText(body, "plain"))

#     for p in (plate_img_path, full_img_path):
#         try:
#             if p and os.path.exists(p):
#                 with open(p, "rb") as f:
#                     part = MIMEBase("application", "octet-stream")
#                     part.set_payload(f.read())
#                     encoders.encode_base64(part)
#                     part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(p)}")
#                     msg.attach(part)
#         except Exception as e:
#             print("⚠️ Attachment error:", e)

#     try:
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login(sender_email, sender_pass)
#             server.send_message(msg)
#             print(f"📧 Email sent for {plate_no} to {receiver_email}")
#     except Exception as e:
#         print("❌ Email sending failed:", e)

# # ---------------- UPDATE CHALLAN ----------------
# def update_challan(final_plate, violation_type, output_folder):
#     df = load_database()
#     existing = set(df["Name"].astype(str) + "_" + df["Surname"].astype(str) + "_" + df["Phone"].astype(str))

#     if final_plate in df["Number Plate"].values:
#         df.loc[df["Number Plate"] == final_plate, "Challan"] += CHALLAN_INCREMENT
#         df.loc[df["Number Plate"] == final_plate, "Violation Type"] = violation_type
#         print(f"⚠️ Existing plate — ₹{CHALLAN_INCREMENT} added.")
#     else:
#         n, s, p = generate_dummy_info(existing)
#         new_entry = {
#             "Number Plate": final_plate,
#             "Name": n, "Surname": s, "Phone": p,
#             "Challan": 500, "Violation Type": violation_type
#         }
#         df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
#         print(f"✅ New record added for {final_plate} — ₹500 challan issued ({violation_type}).")

#     save_database(df)
#     print(f"💾 Database updated ({len(df)} total records)\n")

#     # Attempt to send email (if credentials present)
#     try:
#         record = df[df["Number Plate"] == final_plate].iloc[-1]
#         plate_img = str(Path(output_folder) / "plates" / "plate_best_20.jpg")
#         full_img = str(Path(output_folder) / "full_frames" / "full_best_10.jpg")
#         send_challan_email(record["Name"], record["Surname"], record["Phone"],
#                            record["Number Plate"], record["Challan"],
#                            plate_img, full_img, violation_type)
#     except Exception as e:
#         print("❌ Error while sending challan email:", e)

# # ---------------- MAIN ----------------
# def main(output_dir=None):
#     outputs = Path("outputs")
#     if not outputs.exists():
#         print("❌ No outputs folder found!")
#         return

#     latest_folder = Path(output_dir) if output_dir else max(outputs.glob("*"), key=os.path.getctime)
#     PLATES_DIR = latest_folder / "plates"
#     if not PLATES_DIR.exists():
#         print(f"❌ Plates folder missing in {latest_folder}")
#         return

#     vf = latest_folder / "violation.txt"
#     violation_type = vf.read_text().strip() if vf.exists() else "Unknown Violation"

#     print("🔧 Loading OCR engine (EasyOCR CPU)...")
#     reader = READER
#     print("✅ OCR engine ready\n")

#     images = [f for f in os.listdir(PLATES_DIR) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
#     print(f"🔍 Found {len(images)} plate images in {PLATES_DIR}\n")

#     all_candidates = []
#     for i, fname in enumerate(images, 1):
#         path = PLATES_DIR / fname
#         img = cv2.imread(str(path))
#         if img is None:
#             print(f"[{i}] ⚠️ Skipping unreadable file: {fname}")
#             continue

#         plate = ocr_multi_read(img, reader, reads=READS_PER_IMAGE)
#         if plate:
#             all_candidates.append(plate)
#             print(f"[{i}] ✅ Plate detected: {plate}")
#         else:
#             print(f"[{i}] ❌ No plate detected in {fname}")

#     if not all_candidates:
#         print("\n❌ No number plate detected in entire folder.")
#         return

#     final_plate = merge_with_locking(all_candidates)
#     final_plate = fix_plate_format(final_plate)

#     print("\n---------------------------------------")
#     print("🧩 Detected candidates:")
#     for c in all_candidates:
#         print("   ", c)
#     print("---------------------------------------")
#     print(f"✅ FINAL VERIFIED NUMBER PLATE: {final_plate}")
#     print("---------------------------------------")

#     update_challan(final_plate, violation_type, latest_folder)

#     # Try to update dashboard (keeps your original integration)
#     try:
#         import dashboard_generator
#         dashboard_generator.generate_dashboard()
#         print("📊 Dashboard updated.")
#     except Exception as e:
#         print("⚠️ Could not update dashboard:", e)

# # ---------------- RUN ----------------
# if __name__ == "__main__":
#     import argparse
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--output_dir", type=str)
#     args = parser.parse_args()
#     main(args.output_dir)


















