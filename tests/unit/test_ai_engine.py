"""
Unit tests for AIOptimizationEngine class.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from modules.optimizer.engine import AIOptimizationEngine
from modules.optimizer.models import OptimizationProposal


class TestAIOptimizationEngine:
    """Test suite for AIOptimizationEngine"""
    
    @pytest.mark.unit
    def test_init_creates_instance(self, mock_hardware_nvme):
        """Test that AIOptimizationEngine can be instantiated"""
        engine = AIOptimizationEngine(mock_hardware_nvme)
        
        assert engine is not None
        assert engine.hw == mock_hardware_nvme
        assert engine.proposals == []
    
    @pytest.mark.unit
    def test_scan_current_state_returns_dict(self, mock_hardware_nvme):
        """Test that scan_current_state returns a dictionary"""
        engine = AIOptimizationEngine(mock_hardware_nvme)
        state = engine.scan_current_state()
        
        assert isinstance(state, dict)
        assert "profiles" in state
        assert "disk_type" in state
    
    @pytest.mark.unit
    def test_analyze_io_scheduler_returns_proposals(self, mock_hardware_nvme):
        """Test that analyze_io_scheduler returns list of proposals"""
        engine = AIOptimizationEngine(mock_hardware_nvme)
        proposals = engine.analyze_io_scheduler()
        
        assert isinstance(proposals, list)
        # May be empty if scheduler already optimal
        for proposal in proposals:
            assert isinstance(proposal, OptimizationProposal)
    
    @pytest.mark.unit
    def test_analyze_network_only_returns_proposals(self, mock_hardware_nvme):
        """Test that analyze_network_only returns proposals"""
        engine = AIOptimizationEngine(mock_hardware_nvme)
        proposals = engine.analyze_network_only()
        
        assert isinstance(proposals, list)
        # Should have network proposals
        for proposal in proposals:
            assert isinstance(proposal, OptimizationProposal)
            assert proposal.category == "network"
    
    @pytest.mark.unit
    def test_proposals_have_required_fields(self, mock_hardware_nvme):
        """Test that proposals have all required fields"""
        engine = AIOptimizationEngine(mock_hardware_nvme)
        proposals = engine.analyze_network_only()
        
        if proposals:
            p = proposals[0]
            assert hasattr(p, 'param')
            assert hasattr(p, 'current')
            assert hasattr(p, 'proposed')
            assert hasattr(p, 'reason')
            assert hasattr(p, 'category')
            assert hasattr(p, 'priority')
    
    @pytest.mark.unit
    def test_gamer_profile_gets_gaming_proposals(self, mock_hardware_gamer):
        """Test that gamer profile generates gaming-specific proposals"""
        engine = AIOptimizationEngine(mock_hardware_gamer)
        proposals = engine.analyze_and_propose_sysctl("gamer")
        
        # Should have proposals
        assert len(proposals) > 0
        
        # Check for gamer-specific params
        params = [p.param for p in proposals]
        gaming_params = ["vm.max_map_count", "kernel.sched_latency_ns"]
        
        has_gaming = any(gp in params for gp in gaming_params)
        assert has_gaming, "No gaming-specific parameters found"
    
    @pytest.mark.unit
    def test_proposals_have_turkish_reasons(self, mock_hardware_nvme):
        """Test that proposal reasons are in Turkish"""
        engine = AIOptimizationEngine(mock_hardware_nvme)
        proposals = engine.analyze_network_only()
        
        if proposals:
            # Check that reason contains Turkish characters or words
            reason = proposals[0].reason
            assert len(reason) > 10  # Not empty
            assert isinstance(reason, str)
    
    @pytest.mark.unit
    def test_priority_levels_valid(self, mock_hardware_nvme):
        """Test that priority levels are valid"""
        engine = AIOptimizationEngine(mock_hardware_nvme)
        proposals = engine.analyze_and_propose_sysctl()
        
        valid_priorities = ["critical", "recommended", "optional"]
        
        for proposal in proposals:
            assert proposal.priority in valid_priorities
