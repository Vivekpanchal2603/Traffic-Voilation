import csv
from pathlib import Path

CSV_FILE = "violations.csv"


def get_all_violations():
    if not Path(CSV_FILE).exists():
        return []

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


def delete_violation_by_id(violation_id: str):
    if not Path(CSV_FILE).exists():
        return False

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    updated_rows = [
        row for row in rows
        if row["violation_id"] != violation_id
    ]

    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "violation_id",
                "timestamp",
                "number_plate",
                "helmet_violation",
                "triple_seat_violation",
                "phone_violation",
                "fine_amount"
            ]
        )

        writer.writeheader()
        writer.writerows(updated_rows)

    return True