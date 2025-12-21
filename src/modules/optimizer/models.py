"""
Data models for the optimizer module.
Contains dataclasses for proposals and transactions.
"""
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class OptimizationProposal:
    """Single optimization change with AI-generated explanation"""
    param: str           # Parameter name (e.g., "vm.swappiness")
    current: str         # Current value
    proposed: str        # Proposed optimal value
    reason: str          # WHY this change is needed (Turkish)
    category: str        # "memory", "network", "scheduler", "disk", "boot"
    priority: str        # "critical", "recommended", "optional"
    command: str = ""    # Command to apply (for non-sysctl)

@dataclass
class OptimizationTransaction:
    """Record of applied optimization changes for rollback"""
    id: str                          # Unique transaction ID
    timestamp: str                   # When applied
    category: str                    # "quick", "kernel", "network", "io", "gaming"
    description: str                 # Human-readable description
    changes: List[Dict] = field(default_factory=list)  # [{param, old, new}]
