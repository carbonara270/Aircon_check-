from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Aircon checker backend is running."

@app.route("/run", methods=["POST"])
def run_checker():
    return jsonify({
        "message": "Backend received request successfully."
    })
