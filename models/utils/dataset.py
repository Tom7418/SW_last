import os
import numpy as np

class EMBERDataset:
    def __init__(self, data_dir, subset="train", feature_version=2):
        self.data_dir = data_dir
        self.subset = subset
        self.feature_version = feature_version

        self.X_path = os.path.join(data_dir, f"X_{subset}.dat")
        self.y_path = os.path.join(data_dir, f"y_{subset}.dat")

        if not os.path.exists(self.X_path) or not os.path.exists(self.y_path):
            raise FileNotFoundError("Vectorized data files not found.")

    def __len__(self):
        return self.num_samples()

    def __getitem__(self, idx):
        with open(self.X_path, "rb") as fx, open(self.y_path, "rb") as fy:
            fx.seek(idx * 2381)  # EMBER feature size
            fy.seek(idx * 1)
            x = np.frombuffer(fx.read(2381), dtype=np.uint8)
            y = np.frombuffer(fy.read(1), dtype=np.uint8)[0]
            return x, y

    def num_samples(self):
        return os.path.getsize(self.y_path)


