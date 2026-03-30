from flask import Flask, request, abort
import hashlib

app = Flask(__name__)

REAL_FLAG = "FLAG{I_love_Defense}"
SECRET_SALT = "x9a!Kp#3LmZ"

def generate_key():
    return hashlib.sha256("admin_access_granted".encode()).hexdigest()

def generate_token(key):
    return hashlib.sha256((key + SECRET_SALT).encode()).hexdigest()

@app.route("/get_flag")
def get_flag():
    key = request.args.get("key")
    token = request.args.get("token")

    if not key or not token:
        abort(403)

    real_key = generate_key()
    real_token = generate_token(real_key)

    if key == real_key and token == real_token:
        return REAL_FLAG

    abort(403)
