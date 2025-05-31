import numpy as np
from utils.dataset import EMBERDataset

def convert_to_npz(data_dir="./ember_data", save_path="ember_vectorized_data.npz"):
    # EMBERDataset은 벡터화된 데이터셋을 자동으로 로드함
    train_data = EMBERDataset(data_dir, subset="train", feature_version=2)
    test_data = EMBERDataset(data_dir, subset="test", feature_version=2)

    X_train, y_train = zip(*train_data)
    X_test, y_test = zip(*test_data)

    X = np.vstack(X_train + X_test)
    y = np.hstack(y_train + y_test)

    np.savez_compressed(save_path, X=X, y=y)
    print(f"✅ 저장 완료: {save_path}")

if __name__ == "__main__":
    convert_to_npz()
