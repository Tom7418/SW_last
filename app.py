# app.py

from flask import Flask, request, render_template
import os
import zipfile
import hashlib
import json

# Ember + AI 모델 관련 import
import joblib
from ember.features import PEFeatureExtractor
import numpy as np

app = Flask(__name__)

# ─────────── 1) 설정 파트 ───────────
# (1) 업로드 임시 폴더
UPLOAD_FOLDER = 'temp/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# (2) AI 모델 경로 (학습 후 저장된 .pkl 파일)
MODEL_PATH = 'model/ransomware_model.pkl'  # 실제 경로/파일명으로 맞춰주세요

# (3) Ember PEFeatureExtractor 객체 생성
#     feature_version=2 → Ember 2.x 규격(2381차원) 특징 벡터
EXTRACTOR = PEFeatureExtractor(feature_version=2)

# (4) AI 모델(랜덤포레스트 등) 로드
try:
    MODEL = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"모델 로딩 실패: {e}")

# (5) 허용할 실행 파일 확장자 (비밀번호가 붙은 .exe.vir/.dll.vir도 포함)
ALLOWED_EXTENSIONS = ('.exe', '.dll', '.exe.vir', '.dll.vir')

# (6) TheZoo 등에서 제공하는 ZIP 암호 (대부분 'infected')
#     실제 사용하는 ZIP의 비밀번호가 다르다면, 여기 여러 개를 리스트로 추가해 두고 순차 시도할 수 있습니다.
ZIP_PASSWORDS = [
    b'infected',    # 기본 TheZoo 샘플 암호
    b'malware',     # 혹시 다른 경우
    b'password123'  # 임시용 예시
]


# ─────────── 2) 헬퍼 함수 ───────────
def calculate_sha256_bytes(data_bytes: bytes) -> str:
    """
    바이트 데이터를 받아 SHA256 해시(hex 문자열) 반환
    """
    return hashlib.sha256(data_bytes).hexdigest()


def analyze_zip_in_memory(zip_path: str):
    """
    ZIP 파일 경로(zip_path)를 받아서 내부에서 허용 확장자(PE)를 가진 항목을 모두 찾아낸 뒤,
    메모리 상에서 읽어 들여(암호화된 경우 pwd 시도) Ember → AI 예측을 수행.
    결과 리스트(dict) 반환.
    """
    results = []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # ZIP 내부 모든 항목 순회
            for info in zip_ref.infolist():
                filename_lower = info.filename.lower()

                # 1) 확장자가 ALLOWED_EXTENSIONS에 해당되는지 확인
                if not filename_lower.endswith(ALLOWED_EXTENSIONS):
                    continue

                # 2) ZIP 내부 항목(파일) 읽기 시도
                raw_bytes = None
                sha256_hex = None

                # 2-1) 비밀번호 없이 시도
                try:
                    with zip_ref.open(info) as fp:
                        raw_bytes = fp.read()
                except RuntimeError as e:
                    # 암호화가 필요하다는 예외가 떴을 때
                    # → 미리 지정해 둔 ZIP_PASSWORDS 리스트 중 하나씩 시도
                    for pwd in ZIP_PASSWORDS:
                        try:
                            with zip_ref.open(info, pwd=pwd) as fp:
                                raw_bytes = fp.read()
                            # 읽기에 성공하면 반복 종료
                            break
                        except RuntimeError:
                            raw_bytes = None
                        except Exception:
                            raw_bytes = None

                except Exception as e:
                    # ZIP 자체가 손상되었거나 다른 이유로 읽을 수 없는 경우
                    raw_bytes = None

                # 2-2) read 결과가 없으면 “암호화 실패”로 처리하고 다음 항목으로
                if raw_bytes is None:
                    results.append({
                        'filename': info.filename,
                        'sha256': None,
                        'label': '❌ 암호화되어 있어 추출 불가',
                        'detail': 'ZIP 내부 파일이 암호화되어 있거나 읽기 실패'
                    })
                    continue

                # 3) raw_bytes가 확보되었다면 SHA256 계산
                sha256_hex = calculate_sha256_bytes(raw_bytes)

                # 4) Ember 추출 (raw_features → process_raw_features)
                try:
                    raw_feats = EXTRACTOR.raw_features(raw_bytes)
                    feature_vector = EXTRACTOR.process_raw_features(raw_feats)  # 벡터(2381차원)
                except Exception as e:
                    results.append({
                        'filename': info.filename,
                        'sha256': sha256_hex,
                        'label': '❌ PEFeatureExtractor 실패',
                        'detail': f'Ember feature 추출 오류: {e}'
                    })
                    continue

                # 5) AI 모델 예측 (랜덤포레스트 등)
                try:
                    X = feature_vector.reshape(1, -1)   # 2차원 배열: (1, 2381)
                    y_pred = MODEL.predict(X)[0]        # 0 또는 1
                    label_text = '🔴 악성(랜섬웨어 의심)' if int(y_pred) == 1 else '🟢 정상 파일'
                except Exception as e:
                    results.append({
                        'filename': info.filename,
                        'sha256': sha256_hex,
                        'label': '❌ 예측 실패',
                        'detail': f'AI 모델 예측 오류: {e}'
                    })
                    continue

                # 6) 정상적으로 예측까지 완료되었으므로 결과 목록에 추가
                results.append({
                    'filename': info.filename,
                    'sha256': sha256_hex,
                    'label': label_text,
                    'detail': 'AI 모델 예측 완료'
                })

            # ZIP 내부에 한 번도 ALLOWED_EXTENSIONS 매칭 항목이 없으면 빈 리스트 그대로 반환
            return results

    except zipfile.BadZipFile:
        # ZIP 파일 형식이 올바르지 않을 때
        return [{
            'filename': None,
            'sha256': None,
            'label': '❌ ZIP 형식 오류',
            'detail': '올바른 ZIP 아카이브가 아닙니다'
        }]
    except Exception as e:
        return [{
            'filename': None,
            'sha256': None,
            'label': '❌ ZIP 처리 중 오류',
            'detail': f'예외 발생: {e}'
        }]


# ─────────── 3) Flask 라우트 ───────────
@app.route("/", methods=["GET", "POST"])
def upload():
    """
    GET: index.html 렌더링 (results=None)  
    POST: form으로 전달된 ZIP 파일을 임시 저장 → analyze_zip_in_memory 호출 → 결과를 다시 index.html로 렌더링
    """
    results = None

    if request.method == "POST":
        uploaded_file = request.files.get("file", None)

        if not uploaded_file:
            results = [{
                'filename': None,
                'sha256': None,
                'label': '❌ 파일이 없습니다',
                'detail': '업로드된 파일을 찾을 수 없음'
            }]
        else:
            # 1) 반드시 .zip 확장자만 허용
            if not uploaded_file.filename.lower().endswith(".zip"):
                results = [{
                    'filename': None,
                    'sha256': None,
                    'label': '❌ .zip만 허용',
                    'detail': 'ZIP 파일(.zip)만 올려주세요'
                }]
            else:
                # 2) 업로드된 ZIP을 임시 폴더에 저장
                zip_filename = uploaded_file.filename
                zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)
                uploaded_file.save(zip_path)

                # 3) 메모리 기반 ZIP 분석 수행
                results = analyze_zip_in_memory(zip_path)

                # 4) 분석이 끝난 뒤 임시 ZIP 파일 삭제
                try:
                    os.remove(zip_path)
                except OSError:
                    pass

    # 5) index.html 렌더링 시, results 변수를 템플릿에 넘겨 줌
    return render_template("index.html", results=results)


if __name__ == "__main__":
    # Flask 개발 서버 실행 (디버그 모드 ON)
    app.run(host="0.0.0.0", port=5000, debug=True)