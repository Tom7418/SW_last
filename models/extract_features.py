# extract_benign_from_samples.py
import os
import json
from ember.features import PEFeatureExtractor

input_dir = "models/samples"
output_dir = "jsons/benign"

extractor = PEFeatureExtractor(feature_version=2)
os.makedirs(output_dir, exist_ok=True)

count = 0
for filename in os.listdir(input_dir):
    if filename.lower().endswith(".exe"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename + ".json")

        try:
            with open(input_path, "rb") as f:
                bytez = f.read()
            features = extractor.raw_features(bytez)

            with open(output_path, "w", encoding="utf-8") as out:
                json.dump(features, out)

            count += 1
            print(f"[{count:03}] ✅ {filename} → {output_path}")
        except Exception as e:
            print(f"[ERR] ❌ {filename}: {e}")

print(f"\n🎉 총 {count}개 benign 샘플 특징 추출 완료!")
