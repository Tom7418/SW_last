import json
import numpy as np
from ember.features import PEFeatureExtractor

# 1. feature extractor 로딩
extractor = PEFeatureExtractor(feature_version=2)

# 2. JSON 파일 불러오기
with open("extracted/notepad.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

# 3. features.py 기준으로 process_raw_features 적용
x = extractor.process_raw_features(raw)

# 4. npz로 저장
np.savez("converted/converted_notepad.npz", X=x, y=np.array([0]))  # y는 예시로 정상(0)이라고 둠

print("✅ 변환 완료: converted_notepad.npz 로 저장됨")
