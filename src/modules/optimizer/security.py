"""
Security utilities for input validation and sanitization.

CRITICAL: This module provides security functions for a tool running with root privileges.
All user inputs must be validated before being used in system commands.
"""
import re
import os
import stat
from typing import List


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_sysctl_param(param: str) -> bool:
    """
    Validate sysctl parameter name to prevent command injection.
    
    Args:
        param: Parameter name to validate (e.g., "vm.swappiness")
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If parameter name is invalid or potentially malicious
        
    Examples:
        >>> validate_sysctl_param("vm.swappiness")
        True
        >>> validate_sysctl_param("vm.swappiness; rm -rf /")
        ValidationError: Invalid sysctl parameter
    """
    if not param or not isinstance(param, str):
        raise ValidationError("Parameter must be a non-empty string")
    
    # Only allow valid sysctl parameter names
    # Format: lowercase letters, numbers, dots, underscores
    pattern = r'^[a-z0-9_\.]+$'
    
    if not re.match(pattern, param):
        raise ValidationError(
            f"Invalid sysctl parameter: {param}. "
            "Must contain only lowercase letters, numbers, dots, and underscores."
        )
    
    # Additional safety checks
    if param.startswith('.') or param.endswith('.'):
        raise ValidationError(
            f"Invalid sysctl parameter: {param} (cannot start or end with dot)"
        )
    
    if '..' in param:
        raise ValidationError(
            f"Invalid sysctl parameter: {param} (consecutive dots not allowed)"
        )
    
    # Length limit
    if len(param) > 128:
        raise ValidationError(
            f"Invalid sysctl parameter: {param} (too long, max 128 characters)"
        )
    
    return True


def validate_sysctl_value(value: str) -> bool:
    """
    Validate sysctl parameter value to prevent command injection.
    
    Args:
        value: Value to validate (e.g., "10", "bbr")
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If value is invalid or potentially malicious
    """
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    
    # Allow alphanumeric, spaces, dashes, underscores
    # No special shell characters
    pattern = r'^[a-zA-Z0-9\s_\-\.]+$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            f"Invalid sysctl value: {value}. "
            "Must contain only letters, numbers, spaces, dashes, dots, and underscores."
        )
    
    # Check for command injection attempts
    dangerous_chars = [';', '|', '&', '$', '`', '(', ')', '<', '>', '\n', '\r', '\\']
    for char in dangerous_chars:
        if char in value:
            raise ValidationError(
                f"Invalid sysctl value: {value!r} (contains dangerous character {char!r})"
            )
    
    # Length limit
    if len(value) > 256:
        raise ValidationError(
            f"Invalid sysctl value: {value} (too long, max 256 characters)"
        )
    
    return True


def validate_file_path(path: str, allowed_dirs: List[str] = None) -> bool:
    """
    Validate file path for security (prevent path traversal).
    
    Args:
        path: File path to validate
        allowed_dirs: List of allowed directories (optional)
        
    Returns:
        bool: True if valid
        
    Raises:
        ValidationError: If path is invalid or potentially malicious
    """
    if not path or not isinstance(path, str):
        raise ValidationError("Path must be a non-empty string")
    
    # Prevent path traversal
    if '..' in path:
        raise ValidationError(
            f"Invalid path: {path} (contains '..' - path traversal attempt)"
        )
    
    # Must be absolute path
    if not os.path.isabs(path):
        raise ValidationError(
            f"Invalid path: {path} (must be absolute path)"
        )
    
    # Check for null bytes
    if '\x00' in path:
        raise ValidationError(
            f"Invalid path: {path} (contains null byte)"
        )
    
    # Check allowed directories if specified
    if allowed_dirs:
        allowed = any(path.startswith(d) for d in allowed_dirs)
        if not allowed:
            raise ValidationError(
                f"Invalid path: {path} (not in allowed directories: {allowed_dirs})"
            )
    
    return True


def sanitize_string(value: str, max_length: int = 256) -> str:
    """
    Sanitize string input by removing dangerous characters.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized string
    """
    if not isinstance(value, str):
        return ""
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Remove control characters
    value = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n')
    
    # Limit length
    if len(value) > max_length:
        value = value[:max_length]
    
    # Strip whitespace
    value = value.strip()
    
    return value


def write_secure_file(path: str, content: str, mode: int = 0o600) -> None:
    """
    Write file with secure permissions.
    
    Args:
        path: File path
        content: Content to write
        mode: File permissions (default: 0600 = rw-------)
        
    Raises:
        ValidationError: If path is invalid
        PermissionError: If permissions cannot be set correctly
    """
    # Validate path
    allowed_dirs = ['/etc/sysctl.d', '/var/lib/fedoraclean']
    validate_file_path(path, allowed_dirs)
    
    # Create file with restrictive permissions
    fd = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        mode=mode
    )
    
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception:
        os.close(fd)
        raise
    
    # Verify permissions
    st = os.stat(path)
    actual_mode = stat.S_IMODE(st.st_mode)
    
    if actual_mode != mode:
        raise PermissionError(
            f"File {path} has incorrect permissions: {oct(actual_mode)} "
            f"(expected {oct(mode)})"
        )


def ensure_secure_directory(dir_path: str, mode: int = 0o700) -> None:
    """
    Create directory with secure permissions.
    
    Args:
        dir_path: Directory path
        mode: Directory permissions (default: 0700 = rwx------)
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, mode=mode, exist_ok=True)
    
    # Verify and fix permissions
    st = os.stat(dir_path)
    actual_mode = stat.S_IMODE(st.st_mode)
    
    if actual_mode & 0o077:  # Check if group/world has any permissions
        # Fix permissions
        os.chmod(dir_path, mode)
