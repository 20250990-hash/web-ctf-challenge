from flask import Flask, request, abort

app = Flask(__name__)

REAL_FLAG = "FLAG{real_super_secret_flag}"
SECRET_TOKEN = "ctf_secret_777"

@app.route("/")
def home():
    return "CTF FLAG SERVER"

@app.route("/get_flag")
def get_flag():
    key = request.args.get("key")
    token = request.args.get("token")

    if not key or not token:
        abort(403)

    if key == "letmein123" and token == SECRET_TOKEN:
        return REAL_FLAG

    abort(403)

if __name__ == "__main__":
    app.run()
