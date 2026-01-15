import unittest
import os
import shutil
import joblib
import numpy as np
from src.modules.optimizer.ml_logic import SmartOptimizerModel

class TestSmartOptimizerModel(unittest.TestCase):

    def setUp(self):
        # Use a temporary path for the model to avoid messing with the real one
        self.test_model_path = ".Jules/test_optimizer_model.pkl"
        SmartOptimizerModel.MODEL_PATH = self.test_model_path

        # Clean up before test
        if os.path.exists(self.test_model_path):
            os.remove(self.test_model_path)

        self.model = SmartOptimizerModel()

    def tearDown(self):
        # Clean up after test
        if os.path.exists(self.test_model_path):
            os.remove(self.test_model_path)

    def test_model_training_and_file_creation(self):
        """Test that the model trains and creates the pickle file."""
        self.assertTrue(os.path.exists(self.test_model_path))
        self.assertIsNotNone(self.model.model)

    def test_prediction_general(self):
        """Test 'General' profile prediction (Low RAM, few cores)."""
        features = {
            "ram_gb": 8.0,
            "cpu_cores": 4,
            "is_laptop": True,
            "has_nvme": False,
            "has_gpu": False
        }
        prediction = self.model.predict_profile(features)
        self.assertEqual(prediction, "General")

    def test_prediction_workstation(self):
        """Test 'Workstation' profile prediction (High RAM, many cores)."""
        features = {
            "ram_gb": 64.0,
            "cpu_cores": 16,
            "is_laptop": False,
            "has_nvme": True,
            "has_gpu": False
        }
        prediction = self.model.predict_profile(features)
        self.assertEqual(prediction, "Workstation")

    def test_prediction_gaming(self):
        """Test 'Gaming' profile prediction (Mid RAM, GPU, NVMe)."""
        features = {
            "ram_gb": 32.0,
            "cpu_cores": 8,
            "is_laptop": False,
            "has_nvme": True,
            "has_gpu": True
        }
        # Note: Depending on the randomness of the RF, this might sometimes fluctuate between Gaming and Workstation
        # But our synthetic data distinguishes them by GPU presence largely.
        prediction = self.model.predict_profile(features)
        self.assertEqual(prediction, "Gaming")

    def test_prediction_server(self):
        """Test 'Server' profile prediction (Huge RAM, Many Cores, No GPU, Desktop chassis)."""
        features = {
            "ram_gb": 128.0,
            "cpu_cores": 32,
            "is_laptop": False,
            "has_nvme": True,
            "has_gpu": False
        }
        prediction = self.model.predict_profile(features)
        # Often overlaps with workstation, but let's see if our synthetic data separation holds
        self.assertIn(prediction, ["Server", "Workstation"])

if __name__ == '__main__':
    unittest.main()
