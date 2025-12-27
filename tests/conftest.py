"""
Pytest configuration and shared fixtures.
"""
import pytest
from pathlib import Path
from tests.fixtures.mock_hardware import MockHardwareDetector


@pytest.fixture
def mock_hardware_nvme():
    """Mock hardware with NVMe SSD, 16GB RAM, Desktop."""
    return MockHardwareDetector(
        disk_type="nvme",
        ram_gb=16.0,
        chassis="Desktop",
        cpu_vendor="Intel",
        profiles=["General"]
    )


@pytest.fixture
def mock_hardware_gamer():
    """Mock gaming setup with high-end specs."""
    return MockHardwareDetector(
        disk_type="nvme",
        ram_gb=32.0,
        chassis="Desktop",
        cpu_vendor="AMD",
        profiles=["Gamer"]
    )


@pytest.fixture
def mock_hardware_laptop():
    """Mock laptop setup with developer profile."""
    return MockHardwareDetector(
        disk_type="ssd",
        ram_gb=16.0,
        chassis="Laptop",
        cpu_vendor="Intel",
        profiles=["Developer"]
    )


@pytest.fixture
def mock_hardware_server():
    """Mock server setup."""
    return MockHardwareDetector(
        disk_type="nvme",
        ram_gb=64.0,
        chassis="Server",
        cpu_vendor="AMD",
        profiles=["Server"]
    )


@pytest.fixture
def temp_config_dir(tmp_path):
    """Temporary directory for config files."""
    config_dir = tmp_path / "etc" / "sysctl.d"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def mock_transaction_file(tmp_path):
    """Temporary transaction file."""
    trans_dir = tmp_path / "var" / "lib" / "fedoraclean"
    trans_dir.mkdir(parents=True)
    return trans_dir / "transactions.json"
