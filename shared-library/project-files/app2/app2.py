# app1.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.get("/")
def hello():
    return jsonify(
        app="app2",
        message="✨ Welcome to CloudWithVarJosh — app2 ✨",
        subtitle="Your friendly demo microservice",
        tip="Built with Flask · shipped by Jenkins · running in Docker"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)