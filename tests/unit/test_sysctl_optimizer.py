"""
Unit tests for SysctlOptimizer class.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from modules.optimizer.sysctl import SysctlOptimizer


class TestSysctlOptimizer:
    """Test suite for SysctlOptimizer"""
    
    @pytest.mark.unit
    def test_init_creates_instance(self, mock_hardware_nvme):
        """Test that SysctlOptimizer can be instantiated"""
        optimizer = SysctlOptimizer(mock_hardware_nvme)
        assert optimizer is not None
        assert optimizer.hw == mock_hardware_nvme
    
    @pytest.mark.unit
    def test_generate_config_returns_dict(self, mock_hardware_nvme):
        """Test that generate_optimized_config returns a dictionary"""
        optimizer = SysctlOptimizer(mock_hardware_nvme)
        config = optimizer.generate_optimized_config("general")
        
        assert isinstance(config, dict)
        assert len(config) > 0
    
    @pytest.mark.unit
    def test_nvme_gets_low_swappiness(self, mock_hardware_nvme):
        """Test that NVMe disks get low swappiness (5)"""
        optimizer = SysctlOptimizer(mock_hardware_nvme)
        config = optimizer.generate_optimized_config("general")
        
        assert "vm.swappiness" in config
        assert config["vm.swappiness"] == "5"
    
    @pytest.mark.unit
    def test_ssd_gets_medium_swappiness(self, mock_hardware_laptop):
        """Test that SSD disks get medium swappiness (10)"""
        optimizer = SysctlOptimizer(mock_hardware_laptop)
        config = optimizer.generate_optimized_config("general")
        
        assert "vm.swappiness" in config
        assert config["vm.swappiness"] == "10"
    
    @pytest.mark.unit
    @pytest.mark.parametrize("persona,expected_params", [
        ("general", ["vm.swappiness", "net.ipv4.tcp_congestion_control"]),
        ("gamer", ["vm.max_map_count", "kernel.sched_latency_ns"]),
        ("developer", ["fs.inotify.max_user_watches"]),
        ("server", ["net.core.somaxconn"]),
    ])
    def test_persona_specific_params(self, mock_hardware_nvme, persona, expected_params):
        """Test that different personas include their specific parameters"""
        optimizer = SysctlOptimizer(mock_hardware_nvme)
        config = optimizer.generate_optimized_config(persona)
        
        for param in expected_params:
            assert param in config, f"Missing {param} for {persona} persona"
    
    @pytest.mark.unit
    def test_calculate_min_free_kbytes_16gb(self, mock_hardware_nvme):
        """Test min_free_kbytes calculation for 16GB RAM"""
        optimizer = SysctlOptimizer(mock_hardware_nvme)
        min_free = optimizer.calculate_min_free_kbytes()
        
        # sqrt(16384) * 16 ≈ 2048
        assert 2000 <= min_free <= 2100
    
   @pytest.mark.unit
    def test_calculate_min_free_kbytes_32gb(self, mock_hardware_gamer):
        """Test min_free_kbytes calculation for 32GB RAM"""
        optimizer = SysctlOptimizer(mock_hardware_gamer)
        min_free = optimizer.calculate_min_free_kbytes()
        
        # sqrt(32768) * 16 ≈ 2896
        assert 2800 <= min_free <= 3000
    
    @pytest.mark.unit
    def test_bbr_included_in_network_config(self, mock_hardware_nvme):
        """Test that BBR is included in network configuration"""
        optimizer = SysctlOptimizer(mock_hardware_nvme)
        config = optimizer.generate_optimized_config()
        
        assert "net.ipv4.tcp_congestion_control" in config
        assert config["net.ipv4.tcp_congestion_control"] in ["bbr", "bbr2", "bbr3"]
    
    @pytest.mark.unit
    def test_laptop_gets_battery_optimizations(self, mock_hardware_laptop):
        """Test that laptops get battery-friendly settings"""
        optimizer = SysctlOptimizer(mock_hardware_laptop)
        config = optimizer.generate_optimized_config()
        
        # Laptop should have higher dirty_writeback_centisecs for battery
        assert "vm.dirty_writeback_centisecs" in config
        dirty_writeback = int(config["vm.dirty_writeback_centisecs"])
        assert dirty_writeback >= 3000  # At least 30 seconds
    
    @pytest.mark.unit
    def test_config_includes_security_params(self, mock_hardware_nvme):
        """Test that security parameters are included"""
        optimizer = SysctlOptimizer(mock_hardware_nvme)
        config = optimizer.generate_optimized_config()
        
        # Should have at least one security parameter
        security_params = [
            "kernel.dmesg_restrict",
            "kernel.kptr_restrict",
            "kernel.unprivileged_bpf_disabled"
        ]
        
        has_security = any(param in config for param in security_params)
        assert has_security, "No security parameters found in config"
