import csv
from pathlib import Path

DATABASE = Path(__file__).resolve().parent.parent / "database"


def read_table(filename):
    path = DATABASE / filename
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


SKILLS = (
    ("skill_programming", "Programming"),
    ("skill_data_stats", "Data and stats"),
    ("skill_frontend_design", "Frontend design"),
    ("skill_business_pitch", "Business pitch"),
)


def list_names():
    return [row["name"] for row in read_table("student_responses.csv")]


def skill_averages():
    rows = read_table("student_responses.csv")
    count = len(rows)
    averages = []
    for column, label in SKILLS:
        total = sum(int(row[column]) for row in rows)
        average = round(total / count, 2) if count else None
        averages.append({"skill": label, "average": average})
    return averages
