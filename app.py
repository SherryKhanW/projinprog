import os
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from backend.db import check_connection, list_names, skill_averages

app = Flask(__name__)
FRONTEND = Path(__file__).resolve().parent / "frontend"


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


def database_response(loader):
    try:
        return jsonify(loader())
    except Exception as exc:
        message = str(exc).splitlines()[0]
        return jsonify({"error": message}), 503


@app.get("/api/db-status")
def db_status():
    result = check_connection()
    return jsonify(result), (200 if result.get("ok") else 503)


@app.get("/api/names")
def names():
    return database_response(list_names)


@app.get("/api/skill-averages")
def averages():
    return database_response(skill_averages)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("PORT") is None)
