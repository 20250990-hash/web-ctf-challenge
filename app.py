from flask import Flask, request, abort
import hashlib

app = Flask(__name__)

REAL_FLAG = "FLAG{I_love_Defense}"

# ------------------------
# 메인 서버와 동일해야 함
# ------------------------
SHARED_SECRET_KEY = b'\x93\xfa\x17\xab\xcc\x02\x88\x11\xde\x45\x91\xaf\x33\x77\xb0\xca\x18\x9d\xee\x44\x62\x10\x7b\xc8\x91\x2f\xaa\xbe\x01\x92\xef\x77'
SHARED_SECRET_SALT = b'\x88\xab\xcd\x19\xfa\x70\x11\x42\xbe\x99\x33\x14\xef\x27\xaa\x55'

def generate_key():
    return hashlib.sha256(SHARED_SECRET_KEY).hexdigest()

def generate_token(key):
    return hashlib.sha256((key + SHARED_SECRET_SALT.hex()).encode()).hexdigest()

@app.route("/get_flag", methods=["POST"])
def get_flag():
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
