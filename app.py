import os
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from backend.db import list_names, skill_averages

app = Flask(__name__)
FRONTEND = Path(__file__).resolve().parent / "frontend"


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.get("/api/names")
def names():
    return jsonify(list_names())


@app.get("/api/skill-averages")
def averages():
    return jsonify(skill_averages())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("PORT") is None)
