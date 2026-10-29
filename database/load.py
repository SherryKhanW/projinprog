"""Create the class tables and load the CSV files into DATABASE_URL."""

import csv
import os
import sys
from pathlib import Path

import psycopg
from psycopg import ClientCursor

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.db import load_dotenv
DATABASE = ROOT / "database"
SCHEMA = ROOT / "class_dataset.sql"
MISSING_WORKING_STYLE = "Not provided"


def read_csv(filename):
    with (DATABASE / filename).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main():
    load_dotenv()
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is not set")

    responses = read_csv("student_responses.csv")
    replaced = []
    for row in responses:
        if row["working_style"] == "#NAME?":
            row["working_style"] = MISSING_WORKING_STYLE
            replaced.append(row["name"])

    with psycopg.connect(url, cursor_factory=ClientCursor) as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA.read_text(encoding="utf-8"))
            cur.executemany(
                """
                INSERT INTO student_responses (
                    netid, name, school_year, intro_programming,
                    skill_programming, skill_data_stats, skill_frontend_design,
                    skill_business_pitch, working_style, interests, semester_goal,
                    submitted_at
                ) VALUES (
                    %(netid)s, %(name)s, %(school_year)s, %(intro_programming)s,
                    %(skill_programming)s, %(skill_data_stats)s, %(skill_frontend_design)s,
                    %(skill_business_pitch)s, %(working_style)s, %(interests)s,
                    %(semester_goal)s, %(submitted_at)s
                )
                """,
                responses,
            )
            cur.executemany(
                "INSERT INTO student_tools (netid, tool) VALUES (%(netid)s, %(tool)s)",
                read_csv("student_tools.csv"),
            )
            cur.executemany(
                "INSERT INTO student_availability (netid, slot) VALUES (%(netid)s, %(slot)s)",
                read_csv("student_availability.csv"),
            )
            cur.execute("SELECT name FROM student_responses ORDER BY name")
            names = [row[0] for row in cur.fetchall()]

    print(f"Loaded {len(names)} students.")
    for name in names:
        print(name)
    if replaced:
        print("Replaced spreadsheet error #NAME? in working_style for: " + ", ".join(replaced))


if __name__ == "__main__":
    main()
