import sys
import os

# ✅ features.py 경로 강제 삽입
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../models/ember/ember")))

from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import joblib
from features import PEFeatureExtractor
import features

print("🧠 로딩된 features.py 경로:", features.__file__)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
MODEL_PATH = "converted/malware_model.pkl"

# 📁 폴더 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🧠 모델 로딩
try:
    model = joblib.load(MODEL_PATH)
    extractor = PEFeatureExtractor(feature_version=2)
    print("✅ 모델 로딩 완료")
except Exception as e:
    model = None
    print(f"❌ 모델 로딩 실패: {e}")

# ✅ 누적 검사 결과 리스트
scan_history = []

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename.endswith(".exe"):
            result = "❌ .exe 파일만 업로드 가능합니다."
        else:
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

                # ✅ 누적 리스트에 추가 (최신이 위로)
                scan_history.insert(0, result)

            except Exception as e:
                result = f"⚠️ 분석 중 오류 발생: {str(e)}"
            finally:
                if os.path.exists(save_path):
                    os.remove(save_path)

    return render_template("index.html", result=result, history=scan_history)

@app.route("/model-status")
def model_status():
    try:
        _ = model.predict([[0]*model.n_features_in_])
        return "✅ 모델 정상 작동 중"
    except Exception as e:
        return f"❌ 모델 문제 발생: {e}"

if __name__ == "__main__":
    app.run(debug=True)
