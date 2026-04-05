from flask import Flask, request, jsonify
import base64
import os
import secrets
import time

app = Flask(__name__)

SHARED_SECRET = os.environ.get('CTF_SHARED_SECRET', 'defense-love-secret-2024')
TOKEN_TTL     = int(os.environ.get('TOKEN_TTL', '30'))   # 기본 30초

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, 'flag_image.png')

_TOKEN_STORE: dict[str, float] = {}


def _cleanup_expired():
    now = time.time()
    expired = [t for t, exp in _TOKEN_STORE.items() if now > exp]
    for t in expired:
        del _TOKEN_STORE[t]


def _register_token(token: str):
    _cleanup_expired()
    _TOKEN_STORE[token] = time.time() + TOKEN_TTL


def _consume_token(token: str) -> bool:
    _cleanup_expired()
    if token not in _TOKEN_STORE:
        return False
    if time.time() > _TOKEN_STORE[token]:
        del _TOKEN_STORE[token]
        return False
    del _TOKEN_STORE[token]
    return True

def _image_b64() -> str:
    with open(IMAGE_PATH, 'rb') as f:
        return base64.b64encode(f.read()).decode()

@app.route('/')
def index():
    return _forbidden_page(), 403

@app.route('/api/register-token', methods=['POST'])
def api_register_token():

    if request.headers.get('X-CTF-Secret', '') != SHARED_SECRET:
        return jsonify({'ok': False, 'reason': 'unauthorized'}), 401

    data  = request.get_json(silent=True) or {}
    token = data.get('token', '').strip()
    if not token:
        return jsonify({'ok': False, 'reason': 'token missing'}), 400

    _register_token(token)
    return jsonify({'ok': True}), 200



@app.route('/flag')
def flag():
    token = request.args.get('token', '').strip()

    if not token:
        return _forbidden_page(), 403

    if not _consume_token(token):
        return _forbidden_page(), 403

    return _success_page(_image_b64())


def _forbidden_page() -> str:
    return '''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>403 — 접근 거부</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: "DM Sans", sans-serif;
      background: #fef2f2; color: #1a2744;
      min-height: 100vh;
      display: flex; align-items: center; justify-content: center; text-align: center;
    }
    .wrap { max-width: 420px; padding: 40px; }
    .icon { font-size: 64px; margin-bottom: 24px; }
    h1 {
      font-family: "DM Serif Display", serif;
      font-size: 28px; color: #b91c1c; margin-bottom: 12px;
    }
    p { font-size: 14px; color: #6b7a99; line-height: 1.8; }
    .badge {
      display: inline-block; margin-top: 20px;
      background: #fecaca; color: #b91c1c;
      font-size: 11px; font-weight: 600; letter-spacing: 1px;
      padding: 4px 12px; border-radius: 100px; text-transform: uppercase;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="icon">🚫</div>
    <h1>접근 거부</h1>
    <p>
      유효하지 않거나 만료된 접근입니다.<br>
      2차 인증을 완료해야만 이 페이지에 접근할 수 있습니다.<br>
      URL을 직접 입력하거나 복사해도 접근이 불가능합니다.
    </p>
    <span class="badge">403 Forbidden</span>
  </div>
</body>
</html>'''


def _success_page(img_b64: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>🏴 챌린지 완료 — Defense Love</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --navy: #1a2744; --indigo: #2d4090; --indigo-mid: #3d55b8;
      --indigo-light: #e8ecf8; --indigo-xlight: #f4f6fc; --border: #dde3f0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "DM Sans", sans-serif;
      background: var(--indigo-xlight); color: var(--navy);
      min-height: 100vh;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      padding: 80px 20px 40px;
    }}
    nav {{
      position: fixed; top: 0; left: 0; right: 0; height: 64px;
      display: flex; align-items: center; justify-content: space-between;
      padding: 0 56px;
      background: rgba(255,255,255,0.92); backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border); z-index: 100;
    }}
    .nav-logo {{ font-family: "DM Serif Display", serif; font-size: 20px; color: var(--navy); }}
    .nav-logo span {{ color: var(--indigo-mid); }}
    .wrap {{ width: 100%; max-width: 700px; text-align: center; }}
    .icon-wrap {{
      width: 72px; height: 72px; border-radius: 50%;
      background: #f0fdf4; border: 2px solid #bbf7d0;
      display: flex; align-items: center; justify-content: center;
      margin: 0 auto 24px;
      animation: popIn 0.5s cubic-bezier(0.34,1.56,0.64,1) both;
    }}
    @keyframes popIn {{ from{{opacity:0;transform:scale(0.5)}} to{{opacity:1;transform:scale(1)}} }}
    h1 {{
      font-family: "DM Serif Display", serif; font-size: 32px;
      color: var(--navy); margin-bottom: 10px; letter-spacing: -0.5px;
    }}
    .subtitle {{ font-size: 14px; color: #6b7a99; margin-bottom: 32px; line-height: 1.6; }}
    .img-card {{
      background: #fff; border: 1px solid var(--border);
      border-radius: 20px; overflow: hidden;
      box-shadow: 0 8px 40px rgba(26,39,68,0.12);
      margin-bottom: 28px;
    }}
    .img-card img {{ width: 100%; display: block; }}
    .summary-card {{
      background: #fff; border: 1px solid var(--border);
      border-radius: 16px; padding: 24px 28px;
      box-shadow: 0 2px 16px rgba(26,39,68,0.07); text-align: left;
    }}
    .summary-label {{
      font-size: 10px; font-weight: 700; letter-spacing: 2px;
      text-transform: uppercase; color: var(--indigo-mid); margin-bottom: 12px;
      display: flex; align-items: center; gap: 6px;
    }}
    .summary-label::before {{
      content:""; display:block; width:3px; height:12px;
      background:var(--indigo-mid); border-radius:2px;
    }}
    .summary-row {{ font-size: 13px; color: #6b7a99; line-height: 2.2; }}
    .summary-row strong {{ color: var(--indigo-mid); }}
    @keyframes fadeUp {{ from{{opacity:0;transform:translateY(16px)}} to{{opacity:1;transform:translateY(0)}} }}
    .fade-up {{ animation: fadeUp 0.4s ease both; }}
    .d1{{animation-delay:.1s}} .d2{{animation-delay:.2s}} .d3{{animation-delay:.3s}} .d4{{animation-delay:.4s}}
  </style>
</head>
<body>
<nav>
  <div class="nav-logo">Defense<span>Love</span></div>
</nav>
<div class="wrap">
  <div class="icon-wrap fade-up d1">
    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
      <path d="M6 16l7 7L26 9" stroke="#15803d" stroke-width="2.5"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>
  <h1 class="fade-up d2">🏴 챌린지 완료!</h1>
  <p class="subtitle fade-up d3">
    SQL Injection과 SSTI를 통해 모든 단계를 클리어했습니다.<br>
    이미지 안에서 플래그를 찾아보세요.
  </p>
  <div class="img-card fade-up d3">
    <img src="data:image/png;base64,{img_b64}" alt="flag">
  </div>
  <div class="summary-card fade-up d4">
    <div class="summary-label">클리어 요약</div>
    <div class="summary-row">
      <strong>Stage 1.</strong> SQL Injection — 필터를 우회해 admin 계정 인증 우회<br>
      <strong>Stage 2.</strong> SSTI — 서버 파일을 읽어 2차 인증 코드 획득<br>
      <strong>Flag.</strong> 이미지 안에 숨겨진 플래그를 확인하세요.
    </div>
  </div>
</div>
</body>
</html>'''

if __name__ == '__main__':
    if not os.path.exists(IMAGE_PATH):
        print(f'[!] 이미지 파일 없음: {IMAGE_PATH}')
        raise SystemExit(1)
    if SHARED_SECRET == 'defense-love-secret-2024':
        print('[!] 경고: 기본 SHARED_SECRET 사용 중. 환경변수로 변경하세요.')
    port = int(os.environ.get('PORT', 6000))
    print(f'[*] 플래그 서버 시작: port {port}')
    app.run(host='0.0.0.0', port=port, debug=False)
