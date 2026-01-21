import os
from flask import Flask

app = Flask(__name__)

@app.get("/")
def home():
    return "✅ Bot Running"

@app.get("/health")
def health():
    return "ok"
