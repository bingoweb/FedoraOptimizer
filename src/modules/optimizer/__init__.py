"""
Fedora Optimizer Package - Modular AI-powered system optimization.

Core logic for system scanning, analysis, and optimization.
"""

from .facade import FedoraOptimizer
from .hardware import HardwareDetector
from .sysctl import SysctlOptimizer
from .io_scheduler import IOSchedulerOptimizer
from .backup import OptimizationBackup
from .transaction import TransactionManager
from .engine import AIOptimizationEngine
from .models import OptimizationProposal, OptimizationTransaction
from .system_profiler import SystemProfiler
from .dnf_optimizer import DNFOptimizer
from .boot_optimizer import BootOptimizer
from .security import (
    validate_sysctl_param,
    validate_sysctl_value,
    ValidationError
)

__all__ = [
    'FedoraOptimizer',
    'HardwareDetector',
    'SysctlOptimizer',
    'IOSchedulerOptimizer',
    'OptimizationBackup',
    'TransactionManager',
    'AIOptimizationEngine',
    'OptimizationProposal',
    'OptimizationTransaction',
    'SystemProfiler',
    'DNFOptimizer',
    'BootOptimizer',
    'validate_sysctl_param',
    'validate_sysctl_value',
    'ValidationError',
]
