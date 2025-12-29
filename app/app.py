# app/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)

@app.route("/health")
def health():
    return "OK", 200

@app.route("/items")
def items():
    count = int(request.args.get("count", 10))
    time.sleep(random.uniform(0.05, 0.2))  # 50-200ms delay
    data = [{"id": i, "name": f"item-{i}"} for i in range(count)]
    return jsonify(data), 200

@app.route("/error")
def error():
    return "Internal Server Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
