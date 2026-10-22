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
    app.run(host="127.0.0.1", port=5000, debug=True)
