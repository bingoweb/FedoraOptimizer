# Fedora Optimizer Test Suite

This directory contains the comprehensive test suite for Fedora Optimizer.

## Structure

```
tests/
├── unit/              # Unit tests for individual modules
├── integration/       # Integration tests for workflows
├── fixtures/          # Mock objects and test data
└── conftest.py        # Shared pytest fixtures
```

## Running Tests

### All Tests
```bash
pytest
```

### With Coverage
```bash
pytest --cov=src/modules/optimizer --cov-report=html
```

### Specific Test File
```bash
pytest tests/unit/test_sysctl_optimizer.py
```

### Specific Test
```bash
pytest tests/unit/test_sysctl_optimizer.py::TestSysctlOptimizer::test_nvme_gets_low_swappiness
```

### By Marker
```bash
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m "not slow"    # Exclude slow tests
```

## Writing Tests

### Test Structure
```python
import pytest

class TestYourModule:
    
    @pytest.mark.unit
    def test_something(self, mock_hardware_nvme):
        # Arrange
        optimizer = YourModule(mock_hardware_nvme)
        
        # Act
        result = optimizer.do_something()
        
        # Assert
        assert result == expected_value
```

### Available Fixtures
- `mock_hardware_nvme`: Desktop with NVMe SSD, 16GB RAM
- `mock_hardware_gamer`: Gaming setup, 32GB RAM
- `mock_hardware_laptop`: Laptop with Developer profile
- `mock_hardware_server`: Server setup, 64GB RAM
- `temp_config_dir`: Temporary directory for configs
- `mock_transaction_file`: Temporary transaction file

### Test Markers
- `@pytest.mark.unit`: Unit test (fast, no I/O)
- `@pytest.mark.integration`: Integration test
- `@pytest.mark.slow`: Slow-running test
- `@pytest.mark.requires_root`: Needs root privileges

## Coverage Goals

- **Minimum:** 50%
- **Target:** 80%
- **Ideal:** 90%+

## CI/CD

Tests run automatically on:
- Every push to `main` or `develop`
- All pull requests
- Python 3.11 and 3.12

## Tips

1. **Keep tests fast**: Mock I/O, subprocess calls
2. **One assertion per test**: Makes failures clear
3. **Use parametrize**: Test multiple scenarios efficiently
4. **Good names**: `test_nvme_gets_low_swappiness` not `test_1`
5. **Arrange-Act-Assert**: Clear test structure
