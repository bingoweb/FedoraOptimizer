"""
Unit tests for HardwareDetector mock.
"""
import pytest
from tests.fixtures.mock_hardware import MockHardwareDetector


class TestMockHardwareDetector:
    """Test suite for MockHardwareDetector"""
    
    @pytest.mark.unit
    def test_init_with_defaults(self):
        """Test initialization with default values"""
        hw = MockHardwareDetector()
        
        assert hw.get_simple_disk_type() == "nvme"
        assert hw.ram_info["total"] == 16.0
        assert hw.chassis == "Desktop"
        assert hw.cpu_microarch["vendor"] == "Intel"
    
    @pytest.mark.unit
    @pytest.mark.parametrize("disk_type", ["nvme", "ssd", "hdd"])
    def test_disk_type_detection(self, disk_type):
        """Test that disk type is correctly set"""
        hw = MockHardwareDetector(disk_type=disk_type)
        assert hw.get_simple_disk_type() == disk_type
    
    @pytest.mark.unit
    def test_workload_profile_gamer(self):
        """Test gamer profile detection"""
        hw = MockHardwareDetector(profiles=["Gamer"])
        profiles = hw.detect_workload_profile()
        
        assert "Gamer" in profiles
    
    @pytest.mark.unit
    def test_workload_profile_multiple(self):
        """Test multiple workload profiles"""
        hw = MockHardwareDetector(profiles=["Gamer", "Developer"])
        profiles = hw.detect_workload_profile()
        
        assert len(profiles) == 2
        assert "Gamer" in profiles
        assert "Developer" in profiles
    
    @pytest.mark.unit
    def test_psi_stats_structure(self):
        """Test that PSI stats have correct structure"""
        hw = MockHardwareDetector()
        psi = hw.get_psi_stats()
        
        assert "cpu" in psi
        assert "memory" in psi
        assert "io" in psi
        assert "some" in psi["cpu"]
        assert "avg10" in psi["cpu"]["some"]
    
    @pytest.mark.unit
    def test_intel_cpu_hybrid(self):
        """Test Intel CPU hybrid detection"""
        hw = MockHardwareDetector(cpu_vendor="Intel")
        
        assert hw.cpu_microarch["vendor"] == "Intel"
        assert hw.cpu_microarch["hybrid"] is True
    
    @pytest.mark.unit
    def test_amd_cpu_not_hybrid(self):
        """Test AMD CPU is not hybrid"""
        hw = MockHardwareDetector(cpu_vendor="AMD")
        
        assert hw.cpu_microarch["vendor"] == "AMD"
        assert hw.cpu_microarch["hybrid"] is False
    
    @pytest.mark.unit
    def test_kernel_features_present(self):
        """Test that kernel features dict is populated"""
        hw = MockHardwareDetector()
        
        assert hw.kernel_features["psi"] is True
        assert hw.kernel_features["io_uring"] is True
        assert "bbr_version" in hw.kernel_features
    
    @pytest.mark.unit
    def test_ram_info_consistency(self):
        """Test RAM info matches initialization"""
        hw = MockHardwareDetector(ram_gb=32.0)
        
        assert hw.ram_info["total"] == 32.0
        assert "type" in hw.ram_info
        assert "speed" in hw.ram_info
    
    @pytest.mark.unit
    def test_chassis_types(self):
        """Test different chassis types"""
        for chassis_type in ["Desktop", "Laptop", "Server"]:
            hw = MockHardwareDetector(chassis=chassis_type)
            assert hw.chassis == chassis_type
