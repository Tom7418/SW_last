import sys
import os
import traceback
import logging
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import joblib

# ✅ features.py 경로 삽입
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../models/ember/ember")))
from features import PEFeatureExtractor
import features

# ✅ 로깅 설정
logging.basicConfig(level=logging.DEBUG)

print("🧠 로딩된 features.py 경로:", features.__file__)

# 📁 설정
UPLOAD_FOLDER = "uploads"
MODEL_PATH = "converted/malware_model.pkl"

app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🧠 모델 로딩
try:
    model = joblib.load(MODEL_PATH)
    extractor = PEFeatureExtractor(feature_version=2)
    print("✅ 모델 로딩 완료")
except Exception as e:
    model = None
    print(f"❌ 모델 로딩 실패: {e}")

# ✅ 검사 이력
scan_history = []

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    phishing_result = ""

    if request.method == "POST":
        file = request.files.get("file")
        phone = request.form.get("phone")

        # 📁 악성코드 분석
        if file and file.filename.endswith(".exe"):
            try:
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)

                with open(save_path, "rb") as f:
                    bytez = f.read()
                raw = extractor.raw_features(bytez)
                vector = extractor.process_raw_features(raw).reshape(1, -1)

                pred = model.predict(vector)[0]
                verdict = "🔴 악성코드" if pred == 1 else "🟢 정상"
                result = f"{filename} → {verdict}"
                scan_history.insert(0, result)

            except Exception as e:
                traceback.print_exc()
                result = f"⚠️ 분석 중 오류 발생: {str(e)}"
            finally:
                if os.path.exists(save_path):
                    os.remove(save_path)

        # ☎️ 전화번호 검사
        if phone:
            phishing_result = check_phone_number(phone)

    return render_template("index.html", result=result, phishing=phishing_result, history=scan_history)

@app.route("/model-status")
def model_status():
    try:
        _ = model.predict([[0] * model.n_features_in_])
        return "✅ 모델 정상 작동 중"
    except Exception as e:
        traceback.print_exc()
        return f"❌ 모델 문제 발생: {e}"

# ✅ 전화번호 검사 함수 (로컬 기준)
def check_phone_number(phone):
    phone = phone.strip().replace("-", "").replace(" ", "")
    if phone.startswith("0"):
        phone = "+82" + phone[1:]
    elif not phone.startswith("+"):
        phone = "+82" + phone

    try:
        with open("spam_numbers.txt", "r", encoding="utf-8") as f:
            spam_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return "🚨 스팸 번호 리스트가 없습니다 (spam_numbers.txt를 생성하세요)"

    if phone in spam_list:
        return f"📞 {phone} → ❗ 보이스피싱 의심 번호입니다"
    else:
        return f"📞 {phone} → ✅ 유효한 번호로 확인됨"

if __name__ == "__main__":
    app.run(debug=True)
