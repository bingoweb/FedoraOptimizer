"""
Machine Learning Logic Module.
Responsible for training, loading, and predicting system profiles using Scikit-Learn.
"""
import os
import logging
import joblib
import numpy as np
from typing import Dict, List, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

logger = logging.getLogger("FedoraOptimizerDebug")

class SmartOptimizerModel:
    """
    AI Model for predicting the optimal system profile.
    Uses Random Forest Classifier trained on synthetic (logic-based) data.
    """

    MODEL_PATH = ".Jules/optimizer_model.pkl"

    # Feature Mapping:
    # [RAM_GB, CPU_CORES, IS_LAPTOP, HAS_NVME, HAS_DEDICATED_GPU]
    # RAM_GB: float
    # CPU_CORES: int
    # IS_LAPTOP: 1 (True) or 0 (False)
    # HAS_NVME: 1 or 0
    # HAS_DEDICATED_GPU: 1 or 0

    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        # Define known classes manually to ensure consistency
        self.label_encoder.fit(["General", "Workstation", "Gaming", "Server"])
        self._ensure_model_exists()

    def _ensure_model_exists(self):
        """Checks if model exists, if not, trains a new one."""
        if os.path.exists(self.MODEL_PATH):
            try:
                self.model = joblib.load(self.MODEL_PATH)
                logger.info("🧠 AI Model loaded successfully.")
            except Exception as e:
                logger.warning(f"Failed to load AI model, retraining: {e}")
                self.train_new_model()
        else:
            logger.info("🧠 No AI Model found. Training initial model...")
            self.train_new_model()

    def train_new_model(self):
        """Generates synthetic data and trains the Random Forest model."""
        X, y = self._generate_synthetic_data()

        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)

        # Ensure .Jules directory exists
        os.makedirs(os.path.dirname(self.MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, self.MODEL_PATH)
        logger.info("🧠 AI Model trained and saved.")

    def _generate_synthetic_data(self):
        """
        Creates synthetic training data based on logical heuristics.
        This bootstraps the model with "common sense".
        """
        data = []
        labels = []

        # Features: [RAM, Cores, IsLaptop, NVMe, DedicatedGPU]

        # 1. Low Spec / General Use
        for _ in range(50):
            ram = np.random.uniform(4, 16)
            cores = np.random.randint(2, 6)
            laptop = np.random.choice([0, 1])
            nvme = np.random.choice([0, 1])
            gpu = 0
            data.append([ram, cores, laptop, nvme, gpu])
            labels.append("General")

        # 2. Workstation (High RAM, Many Cores, No massive GPU req)
        for _ in range(50):
            ram = np.random.uniform(32, 128)
            cores = np.random.randint(8, 32)
            laptop = np.random.choice([0, 1])
            nvme = 1
            gpu = np.random.choice([0, 1])
            data.append([ram, cores, laptop, nvme, gpu])
            labels.append("Workstation")

        # 3. Gaming (Mid-High RAM, NVMe, Dedicated GPU)
        for _ in range(50):
            ram = np.random.uniform(16, 64)
            cores = np.random.randint(6, 16)
            laptop = np.random.choice([0, 1]) # Gaming Laptop or Desktop
            nvme = 1
            gpu = 1
            data.append([ram, cores, laptop, nvme, gpu])
            labels.append("Gaming")

        # 4. Server (High RAM, High Cores, No GPU, Desktop Chassis mainly)
        for _ in range(50):
            ram = np.random.uniform(16, 256)
            cores = np.random.randint(4, 64)
            laptop = 0
            nvme = np.random.choice([0, 1])
            gpu = 0
            data.append([ram, cores, laptop, nvme, gpu])
            labels.append("Server")

        # Encode labels
        y_encoded = self.label_encoder.transform(labels)
        return np.array(data), y_encoded

    def predict_profile(self, features: Dict[str, Any]) -> str:
        """
        Predicts the profile based on extracted features.
        Expected keys in features:
        - ram_gb (float)
        - cpu_cores (int)
        - is_laptop (bool)
        - has_nvme (bool)
        - has_gpu (bool)
        """
        if not self.model:
            logger.error("Model not initialized during prediction.")
            return "General"

        try:
            # Prepare feature vector
            vector = np.array([[
                features.get("ram_gb", 8.0),
                features.get("cpu_cores", 4),
                1 if features.get("is_laptop", False) else 0,
                1 if features.get("has_nvme", False) else 0,
                1 if features.get("has_gpu", False) else 0
            ]])

            prediction_idx = self.model.predict(vector)[0]
            profile_name = self.label_encoder.inverse_transform([prediction_idx])[0]

            # Get probability/confidence
            probs = self.model.predict_proba(vector)[0]
            confidence = probs[prediction_idx] * 100

            logger.info(f"🧠 AI Prediction: {profile_name} (Confidence: {confidence:.1f}%)")

            return profile_name

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return "General"
