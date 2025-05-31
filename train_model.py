import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import joblib
import os

# 1. 데이터 로드
data = np.load("converted/converted_notepad.npz")
X = data["X"]
y = data["y"]

# reshape 처리 추가 (단일 샘플 대응용)
X = X.reshape(1, -1)

# 2. 모델 정의 및 학습
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 3. 예측 및 평가 (지금은 학습셋만 있으므로 평가용은 형식상 사용)
pred = model.predict(X)
acc = accuracy_score(y, pred)
f1 = f1_score(y, pred, average="macro")

# 4. 결과 출력
print(f"✅ 학습 완료! Accuracy: {acc:.4f}, F1-score: {f1:.4f}")

# 5. 모델 저장
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/ransomware_model.pkl")
print("💾 모델 저장 완료: model/ransomware_model.pkl")
