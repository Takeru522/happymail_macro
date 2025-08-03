import json
import csv
import os

# Load config JSON file
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Log sent messages to CSV
def append_to_csv(file_path, row):
    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["user_name", "status", "message"])
        writer.writerow(row)


