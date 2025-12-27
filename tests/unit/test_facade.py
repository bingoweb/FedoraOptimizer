"""
Unit tests for FedoraOptimizer facade.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from modules.optimizer.facade import FedoraOptimizer


class TestFedoraOptimizer:
    """Test suite for FedoraOptimizer facade"""
    
    @pytest.mark.unit
    def test_analyze_usage_persona_returns_tuple(self, monkeypatch):
        """Test that analyze_usage_persona returns (str, float)"""
        # Mock hardware detector
        from tests.fixtures.mock_hardware import MockHardwareDetector
        
        optimizer = FedoraOptimizer.__new__(FedoraOptimizer)
        optimizer.hw = MockHardwareDetector(profiles=["Gamer"])
        
        persona, confidence = optimizer.analyze_usage_persona()
        
        assert isinstance(persona, str)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0
    
    @pytest.mark.unit
    def test_gamer_profile_detection(self, monkeypatch):
        """Test gamer profile is detected correctly"""
        from tests.fixtures.mock_hardware import MockHardwareDetector
        
        optimizer = FedoraOptimizer.__new__(FedoraOptimizer)
        optimizer.hw = MockHardwareDetector(profiles=["Gamer"])
        
        persona, confidence = optimizer.analyze_usage_persona()
        
        assert persona == "Gamer"
        assert confidence >= 0.85
    
    @pytest.mark.unit
    def test_developer_profile_detection(self, monkeypatch):
        """Test developer profile is detected correctly"""
        from tests.fixtures.mock_hardware import MockHardwareDetector
        
        optimizer = FedoraOptimizer.__new__(FedoraOptimizer)
        optimizer.hw = MockHardwareDetector(profiles=["Developer"])
        
        persona, confidence = optimizer.analyze_usage_persona()
        
        assert persona == "Developer"
        assert confidence >= 0.80
    
    @pytest.mark.unit
    def test_server_profile_detection(self, monkeypatch):
        """Test server profile is detected correctly"""
        from tests.fixtures.mock_hardware import MockHardwareDetector
        
        optimizer = FedoraOptimizer.__new__(FedoraOptimizer)
        optimizer.hw = MockHardwareDetector(profiles=["Server"], chassis="Server")
        
        persona, confidence = optimizer.analyze_usage_persona()
        
        assert persona == "Server"
        assert confidence >= 0.90
    
    @pytest.mark.unit
    def test_general_profile_fallback(self, monkeypatch):
        """Test general profile is used as fallback"""
        from tests.fixtures.mock_hardware import MockHardwareDetector
        
        optimizer = FedoraOptimizer.__new__(FedoraOptimizer)
        optimizer.hw = MockHardwareDetector(profiles=["General"])
        
        persona, confidence = optimizer.analyze_usage_persona()
        
        assert persona == "General"
        assert confidence > 0.0
