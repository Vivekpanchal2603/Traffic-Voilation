# from pathlib import Path
# from ultralytics import YOLO
# import cv2

# CLASS_NAMES = ['number plate', 'no helmet', 'helmet', 'helmet', 'bike']

# CONF_THRESH = 0.30
# TOP_PLATE_COUNT = 25
# TOP_FULL_COUNT = 10


# def run_yolo_detection(video_path: str, output_folder: str, weights_path: str):
#     main_model = YOLO(weights_path)

#     cap = cv2.VideoCapture(video_path)

#     if not cap.isOpened():
#         raise Exception("Could not open video")

#     output_folder = Path(output_folder)
#     plates_dir = output_folder / "plates"
#     full_dir = output_folder / "full_frames"

#     plates_dir.mkdir(parents=True, exist_ok=True)
#     full_dir.mkdir(parents=True, exist_ok=True)

#     top_plates = []
#     top_full_frames = []

#     no_helmet_detected = False
#     violation_detected = False

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         results = main_model.predict(
#             frame,
#             conf=CONF_THRESH,
#             verbose=False
#         )

#         boxes = results[0].boxes

#         if boxes is None:
#             continue

#         for box, cls_id, conf in zip(
#             boxes.xyxy,
#             boxes.cls,
#             boxes.conf
#         ):
#             cls_name = CLASS_NAMES[int(cls_id)]
#             confidence = float(conf.cpu().numpy())

#             x1, y1, x2, y2 = map(
#                 int,
#                 box.cpu().numpy()
#             )

#             # No Helmet Detection
#             if cls_name == "no helmet":
#                 no_helmet_detected = True
#                 violation_detected = True

#             # Save Plate Crops
#             if cls_name == "number plate":
#                 plate_crop = frame[y1:y2, x1:x2]

#                 if plate_crop.size > 0:
#                     if len(top_plates) < TOP_PLATE_COUNT:
#                         top_plates.append(
#                             (confidence, plate_crop)
#                         )
#                     else:
#                         min_idx = min(
#                             range(len(top_plates)),
#                             key=lambda i: top_plates[i][0]
#                         )

#                         if confidence > top_plates[min_idx][0]:
#                             top_plates[min_idx] = (
#                                 confidence,
#                                 plate_crop
#                             )

#         # Save Annotated Violation Frames
#         annotated_frame = results[0].plot()

#         if violation_detected:
#             frame_confidence = max(
#                 [float(c.cpu().numpy()) for c in boxes.conf],
#                 default=0
#             )

#             if len(top_full_frames) < TOP_FULL_COUNT:
#                 top_full_frames.append(
#                     (frame_confidence, annotated_frame)
#                 )
#             else:
#                 min_idx = min(
#                     range(len(top_full_frames)),
#                     key=lambda i: top_full_frames[i][0]
#                 )

#                 if frame_confidence > top_full_frames[min_idx][0]:
#                     top_full_frames[min_idx] = (
#                         frame_confidence,
#                         annotated_frame
#                     )

#     cap.release()

#     # Save Plate Images
#     for i, (_, img) in enumerate(top_plates, 1):
#         cv2.imwrite(
#             str(plates_dir / f"plate_best_{i}.jpg"),
#             img
#         )

#     # Save Violation Frames
#     for i, (_, img) in enumerate(top_full_frames, 1):
#         cv2.imwrite(
#             str(full_dir / f"frame_best_{i}.jpg"),
#             img
#         )

#     return {
#         "violation_detected": violation_detected,
#         "no_helmet": no_helmet_detected,
#         "triple_seat": False,
#         "plates_saved": len(top_plates)
#     }







from pathlib import Path
from ultralytics import YOLO
import cv2

CLASS_NAMES = ['number plate', 'no helmet', 'helmet', 'helmet', 'bike']

CONF_THRESH = 0.30
TOP_PLATE_COUNT = 25
TOP_FULL_COUNT = 10


def run_yolo_detection(video_path: str, output_folder: str, weights_path: str):
    main_model = YOLO(weights_path)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception("Could not open video")

    output_folder = Path(output_folder)

    plates_dir = output_folder / "plates"
    full_dir = output_folder / "full_frames"
    triple_dir = output_folder / "triple_crop"

    plates_dir.mkdir(parents=True, exist_ok=True)
    full_dir.mkdir(parents=True, exist_ok=True)
    triple_dir.mkdir(parents=True, exist_ok=True)

    top_plates = []
    top_full_frames = []
    top_triple_crops = []

    no_helmet_detected = False
    violation_detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]

        results = main_model.predict(
            frame,
            conf=CONF_THRESH,
            verbose=False
        )

        boxes = results[0].boxes

        if boxes is None:
            continue

        bike_boxes = []

        for box, cls_id, conf in zip(
            boxes.xyxy,
            boxes.cls,
            boxes.conf
        ):
            cls_name = CLASS_NAMES[int(cls_id)]
            confidence = float(conf.cpu().numpy())

            x1, y1, x2, y2 = map(int, box.cpu().numpy())

            if cls_name == "no helmet":
                no_helmet_detected = True
                violation_detected = True

            if cls_name == "bike":
                bike_boxes.append((confidence, x1, y1, x2, y2))

            if cls_name == "number plate":
                plate_crop = frame[y1:y2, x1:x2]

                if plate_crop.size > 0:
                    if len(top_plates) < TOP_PLATE_COUNT:
                        top_plates.append((confidence, plate_crop))
                    else:
                        min_idx = min(
                            range(len(top_plates)),
                            key=lambda i: top_plates[i][0]
                        )

                        if confidence > top_plates[min_idx][0]:
                            top_plates[min_idx] = (
                                confidence,
                                plate_crop
                            )

        annotated_frame = results[0].plot()

        if violation_detected:
            frame_confidence = max(
                [float(c.cpu().numpy()) for c in boxes.conf],
                default=0
            )

            if len(top_full_frames) < TOP_FULL_COUNT:
                top_full_frames.append(
                    (frame_confidence, annotated_frame)
                )
            else:
                min_idx = min(
                    range(len(top_full_frames)),
                    key=lambda i: top_full_frames[i][0]
                )

                if frame_confidence > top_full_frames[min_idx][0]:
                    top_full_frames[min_idx] = (
                        frame_confidence,
                        annotated_frame
                    )

            # Save Bike Crop for Triple Seat
            if bike_boxes:
                best_bike = max(bike_boxes, key=lambda x: x[0])

                _, x1, y1, x2, y2 = best_bike

                pad_x = int((x2 - x1) * 0.20)
                pad_y_top = int((y2 - y1) * 0.45)
                pad_y_bottom = int((y2 - y1) * 0.10)

                crop_x1 = max(0, x1 - pad_x)
                crop_y1 = max(0, y1 - pad_y_top)
                crop_x2 = min(w, x2 + pad_x)
                crop_y2 = min(h, y2 + pad_y_bottom)

                triple_crop = frame[
                    crop_y1:crop_y2,
                    crop_x1:crop_x2
                ]

                if triple_crop.size > 0:
                    top_triple_crops.append(
                        (frame_confidence, triple_crop)
                    )

    cap.release()

    for i, (_, img) in enumerate(top_plates, 1):
        cv2.imwrite(str(plates_dir / f"plate_best_{i}.jpg"), img)

    for i, (_, img) in enumerate(top_full_frames, 1):
        cv2.imwrite(str(full_dir / f"frame_best_{i}.jpg"), img)

    for i, (_, img) in enumerate(top_triple_crops[:3], 1):
        cv2.imwrite(str(triple_dir / f"triple_crop_{i}.jpg"), img)

    return {
        "violation_detected": violation_detected,
        "no_helmet": no_helmet_detected,
        "triple_seat": False,
        "plates_saved": len(top_plates)
    }