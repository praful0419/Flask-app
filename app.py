from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")

@app.route("/")
def home():
    return jsonify({
        "message": "Hello from CI/CD pipeline!",
        "version": APP_VERSION,
        "hostname": socket.gethostname()
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
