import os
from pathlib import Path

import psycopg

SKILLS = (
    ("skill_programming", "Programming"),
    ("skill_data_stats", "Data and stats"),
    ("skill_frontend_design", "Frontend design"),
    ("skill_business_pitch", "Business pitch"),
)


def load_dotenv():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv()


def database_target():
    """Host and database name from DATABASE_URL, without the password."""
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        return None
    try:
        parsed = psycopg.conninfo.conninfo_to_dict(url)
    except psycopg.ProgrammingError:
        return {"host": "unparsed", "dbname": "", "port": ""}
    return {
        "host": parsed.get("host") or "",
        "port": str(parsed.get("port") or ""),
        "dbname": parsed.get("dbname") or "",
    }


def connect():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Add it to .env for local runs, or to the Railway service variables."
        )
    host = (database_target() or {}).get("host", "")
    on_railway = bool(os.environ.get("RAILWAY_ENVIRONMENT"))
    if host.endswith(".railway.internal") and not on_railway:
        raise RuntimeError(
            "DATABASE_URL points at postgres.railway.internal. That hostname only works "
            "from another service inside the same Railway project. On this computer, open the "
            "Postgres service in Railway, enable Public Networking, and put DATABASE_PUBLIC_URL "
            "in .env instead. Keep the private URL on the deployed Flask service."
        )
    return psycopg.connect(url, connect_timeout=5)


def list_names():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM student_responses ORDER BY name")
            return [row[0] for row in cur.fetchall()]


def skill_averages():
    with connect() as conn:
        with conn.cursor() as cur:
            averages = []
            for column, label in SKILLS:
                cur.execute(f"SELECT ROUND(AVG({column})::numeric, 2) FROM student_responses")
                value = cur.fetchone()[0]
                averages.append({
                    "skill": label,
                    "average": float(value) if value is not None else None,
                })
            return averages


def check_connection():
    target = database_target()
    if target is None:
        return {"ok": False, "error": "DATABASE_URL is not set"}
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM student_responses")
                count = cur.fetchone()[0]
        return {"ok": True, "host": target["host"], "dbname": target["dbname"], "students": count}
    except Exception as exc:
        return {
            "ok": False,
            "host": target["host"],
            "dbname": target["dbname"],
            "error": str(exc).splitlines()[0],
        }


if __name__ == "__main__":
    result = check_connection()
    if result.get("ok"):
        print(
            f"Connected to {result['host']} / {result['dbname']}. "
            f"{result['students']} rows in student_responses."
        )
    else:
        host = result.get("host") or "(no host)"
        error = result.get("error") or ""
        if "does not exist" in error:
            print(f"Connected to {host} / {result.get('dbname')}, but the class tables are missing.")
            print(error)
        else:
            print(f"Not connected ({host}).")
            print(error)
        raise SystemExit(1)
