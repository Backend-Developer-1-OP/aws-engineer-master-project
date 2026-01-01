# app/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import time, random
from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

app = Flask(__name__)
CORS(app)
patch_all()

xray_recorder.configure(service='MasterProjectAPI')
XRayMiddleware(app, xray_recorder)

@app.route("/test-trace")
def test_trace():
    subsegment = xray_recorder.begin_subsegment('manual')
    xray_recorder.end_subsegment()
    return "trace test", 200

@app.route("/health")
def health():
    return "OK", 200

@app.route("/items")
def items():
    count = int(request.args.get("count", 10))
    time.sleep(random.uniform(0.05, 0.2))
    data = [{"id": i, "name": f"item-{i}"} for i in range(count)]
    return jsonify(data), 200

@app.route("/error")
def error():
    return "Internal Server Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
