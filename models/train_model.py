import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from sklearn.metrics import accuracy_score

# 1. npz 파일 불러오기
data = np.load("converted/dataset.npz")
X = data["X"]
y = data["y"]

# 2. 학습/검증 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# 3. 모델 학습
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# 4. 평가
y_pred = clf.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# 5. 모델 저장
joblib.dump(clf, "converted/malware_model.pkl")
print("✅ 모델 저장 완료: malware_model.pkl")

y_pred = clf.predict(X_test)

# 결과 평가
print("📊 혼동 행렬:\n", confusion_matrix(y_test, y_pred))
print("\n📋 상세 리포트:\n", classification_report(y_test, y_pred))
print("🎯 정확도:", accuracy_score(y_test, y_pred))

# 모델 저장
joblib.dump(clf, "converted/malware_model.pkl")
print("✅ 모델 저장 완료: malware_model.pkl")