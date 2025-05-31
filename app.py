from flask import Flask, request, render_template
import os
import zipfile
import hashlib
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'temp/'
HASH_DB_PATH = 'malicious_hashes.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 악성 해시 DB 불러오기
with open(HASH_DB_PATH, 'r') as f:
    malicious_hashes = json.load(f)

# 확장자 목록 (.vir 포함)
target_extensions = (".exe", ".dll", ".exe.vir", ".vir")

# ZIP 분석 함수 (암호 포함 + 메모리 처리)
def analyze_zip_memory(file_path, password=b'infected'):
    results = []
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.setpassword(password)
            for info in zip_ref.infolist():
                if info.filename.endswith(target_extensions):
                    try:
                        with zip_ref.open(info) as f_in:
                            file_bytes = f_in.read()
                            file_hash = hashlib.sha256(file_bytes).hexdigest()
                            verdict = malicious_hashes.get(file_hash, "🟢 정상 파일")
                            display = f"{info.filename}\n  SHA256: {file_hash}\n  결과: {'🔴 ' + verdict if verdict != '🟢 정상 파일' else verdict}"
                            results.append(display)
                    except RuntimeError as e:
                        if "password required" in str(e).lower():
                            results.append(f"{info.filename} → 🔒 암호로 보호된 파일 (분석 실패)")
                        else:
                            results.append(f"{info.filename} → ⚠️ 오류: {str(e)}")
    except Exception as e:
        results.append(f"❌ 전체 ZIP 분석 실패: {str(e)}")
    
    return results

@app.route("/", methods=["GET", "POST"])
def upload():
    result = ""
    if request.method == "POST":
        file = request.files["file"]
        if not file or not file.filename.endswith(".zip"):
            result = "❌ .zip 파일만 업로드 가능합니다."
        else:
            zip_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(zip_path)

            result_lines = analyze_zip_memory(zip_path)
            result = "\n\n".join(result_lines)
            print("🔎 분석 결과:\n", result)

            os.remove(zip_path)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)