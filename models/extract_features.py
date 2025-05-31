# extract_features.py
import argparse
import json
import os
import lief
from ember.features import PEFeatureExtractor

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help='Input .exe file path')
    parser.add_argument('--output', type=str, required=True, help='Output .json path')
    parser.add_argument('--kind', type=str, default="train", help='Kind: train/test/predict')
    args = parser.parse_args()

    # 파일 읽기
    with open(args.input, 'rb') as f:
        bytez = f.read()

    extractor = PEFeatureExtractor(feature_version=2)
    features = extractor.raw_features(bytez)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(features, f)

    print(f"✅ Features extracted to {args.output}")

if __name__ == '__main__':
    main()
