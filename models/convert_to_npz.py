import os
import sys
import json
import numpy as np

# ✅ 로컬 features.py 경로 강제 삽입 (models/ember/ember 기준)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "ember/ember")))

# ✅ 로딩 시도
from features import PEFeatureExtractor
import features
print("✅ 실제 로딩된 features.py 위치:", features.__file__)
    
# 🧠 로드 확인
print("🧠 실제 로드된 features.py 위치:", features.__file__)

# feature extractor 세팅
extractor = PEFeatureExtractor(feature_version=2)

# 현재 파일 기준으로 models 디렉토리 절대 경로
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 상위 폴더로 이동해 jsons/converted 경로 지정
benign_dir = os.path.normpath(os.path.join(BASE_DIR, "../jsons/benign"))
malware_dir = os.path.normpath(os.path.join(BASE_DIR, "../jsons/malware"))
output_npz = os.path.normpath(os.path.join(BASE_DIR, "../converted/dataset.npz"))

X = []
y = []

def load_features_from_folder(folder_path, label_name, label):
    if not os.path.exists(folder_path):
        print(f"⚠️ 경고: {label_name} 폴더가 존재하지 않습니다 → {folder_path}")
        return

    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    if not files:
        print(f"⚠️ 경고: {label_name} 폴더에 JSON 파일이 없습니다 → {folder_path}")
        return

    total = len(files)
    print(f"\n📂 {label_name.upper()} 폴더: 총 {total}개 파일 변환 시작")

    for idx, file_name in enumerate(files, 1):
        file_path = os.path.join(folder_path, file_name)
        print(f"[{label_name[:1].upper()}{idx:03}/{total}] {file_name} 변환 시도 중...", end=" ")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            features = extractor.process_raw_features(raw)
            X.append(features)
            y.append(label)
            print("✅ 성공")
        except Exception as e:
            print(f"❌ 실패 → 이유: {str(e)}")

# benign: 0, malware: 1
load_features_from_folder(benign_dir, label_name="benign", label=0)
load_features_from_folder(malware_dir, label_name="malware", label=1)

if not X:
    print("\n❌ 처리된 JSON 파일이 하나도 없습니다. 변환을 중단합니다.")
else:
    X = np.vstack(X)
    y = np.array(y)

    os.makedirs(os.path.dirname(output_npz), exist_ok=True)
    np.savez_compressed(output_npz, X=X, y=y)

    print(f"\n🎉 전체 변환 완료: {output_npz} 에 저장됨 (총 샘플 수: {len(y)})")
