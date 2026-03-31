# flag_server.py
from flask import Flask, request, abort
import hashlib
import os

app = Flask(__name__)

REAL_FLAG = "FLAG{I_love_Defense}"

# 🔥 절대 노출되면 안 되는 비밀
SECRET_KEY = os.urandom(32)
SECRET_SALT = os.urandom(16)

def generate_key():
    return hashlib.sha256(SECRET_KEY).hexdigest()

def generate_token(key):
    return hashlib.sha256((key + SECRET_SALT.hex()).encode()).hexdigest()

@app.route("/get_flag", methods=["POST"])
def get_flag():
    # 🔥 외부 접근 차단 (중요)
    if request.remote_addr != "127.0.0.1":
        abort(403)

    key = request.form.get("key")
    token = request.form.get("token")

    if not key or not token:
        abort(403)

    real_key = generate_key()
    real_token = generate_token(real_key)

    if key == real_key and token == real_token:
        return REAL_FLAG

    abort(403)

if __name__ == "__main__":
    app.run(port=5001)
