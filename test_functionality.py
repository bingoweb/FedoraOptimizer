#!/usr/bin/env python3
"""
FedoraOptimizer - Comprehensive Functionality Test Suite
Tests all modules for runtime errors and functionality issues
"""

import sys
import os
sys.path.insert(0, 'src')

from rich.console import Console
from rich.table import Table

console = Console()

# Test Results Tracker
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_section(name):
    """Decorator for test sections"""
    console.print(f"\n[bold cyan]{'='*60}[/]")
    console.print(f"[bold cyan]Testing: {name}[/]")
    console.print(f"[bold cyan]{'='*60}[/]\n")

def test_imports():
    """Test 1: Module Imports"""
    test_section("Module Imports")
    
    try:
        from modules.optimizer import (
            FedoraOptimizer, HardwareDetector, AIOptimizationEngine,
            SysctlOptimizer, IOSchedulerOptimizer, TransactionManager,
            OptimizationBackup, OptimizationProposal
        )
        from modules.utils import run_command, console as utils_console, Theme
        from modules.gaming import GamingOptimizer
        
        console.print("✅ All core imports successful")
        results["passed"].append("Imports: All modules")
        return True
    except Exception as e:
        console.print(f"❌ Import failed: {e}")
        results["failed"].append(f"Imports: {e}")
        return False

def test_hardware_detector():
    """Test 2: HardwareDetector"""
    test_section("HardwareDetector")
    
    try:
        from modules.optimizer import HardwareDetector
        hw = HardwareDetector()
        
        # Test basic attributes
        assert hasattr(hw, 'cpu_info'), "Missing cpu_info"
        assert hasattr(hw, 'ram_info'), "Missing ram_info"
        assert hasattr(hw, 'gpu_info'), "Missing gpu_info"
        assert hasattr(hw, 'disk_info'), "Missing disk_info"
        assert hasattr(hw, 'chassis'), "Missing chassis"
        
        console.print(f"✅ CPU: {hw.cpu_info['model'][:60]}...")
        console.print(f"✅ RAM: {hw.ram_info['total']} GB {hw.ram_info['type']}")
        console.print(f"✅ GPU: {hw.gpu_info}")
        console.print(f"✅ Disk: {hw.disk_info}")
        console.print(f"✅ Chassis: {hw.chassis}")
        
        # Test methods
        disk_type = hw.get_simple_disk_type()
        console.print(f"✅ Disk Type: {disk_type}")
        
        profiles = hw.detect_workload_profile()
        console.print(f"✅ Workload Profiles: {', '.join(profiles)}")
        
        results["passed"].append("HardwareDetector: All attributes and methods")
        return True
    except Exception as e:
        console.print(f"❌ HardwareDetector failed: {e}")
        import traceback
        traceback.print_exc()
        results["failed"].append(f"HardwareDetector: {e}")
        return False

def test_sysctl_optimizer():
    """Test 3: SysctlOptimizer"""
    test_section("SysctlOptimizer")
    
    try:
        from modules.optimizer import SysctlOptimizer, HardwareDetector
        hw = HardwareDetector()
        sysctl = SysctlOptimizer(hw)
        
        # Test config generation
        config = sysctl.generate_optimized_config('general')
        console.print(f"✅ Generated {len(config)} sysctl parameters")
        
        # Check key parameters
        assert 'vm.swappiness' in config, "Missing vm.swappiness"
        assert 'net.ipv4.tcp_congestion_control' in config, "Missing BBR config"
        
        console.print(f"  - vm.swappiness: {config['vm.swappiness']}")
        console.print(f"  - tcp_congestion_control: {config['net.ipv4.tcp_congestion_control']}")
        
        # Test min_free_kbytes calculation
        min_free = sysctl.calculate_min_free_kbytes()
        console.print(f"✅ Calculated min_free_kbytes: {min_free} KB")
        
        results["passed"].append("SysctlOptimizer: Config generation and calculations")
        return True
    except Exception as e:
        console.print(f"❌ SysctlOptimizer failed: {e}")
        import traceback
        traceback.print_exc()
        results["failed"].append(f"SysctlOptimizer: {e}")
        return False

def test_ai_engine():
    """Test 4: AIOptimizationEngine"""
    test_section("AIOptimizationEngine")
    
    try:
        from modules.optimizer import AIOptimizationEngine, HardwareDetector
        hw = HardwareDetector()
        ai = AIOptimizationEngine(hw)
        
        # Test proposal generation
        proposals = ai.analyze_and_propose_sysctl('general')
        console.print(f"✅ Generated {len(proposals)} optimization proposals")
        
        if proposals:
            for i, p in enumerate(proposals[:3], 1):
                console.print(f"  {i}. {p.param}: {p.current} → {p.proposed} ({p.priority})")
                console.print(f"     Reason: {p.reason[:60]}...")
        else:
            console.print("  ℹ️  No proposals (system may already be optimized)")
            results["warnings"].append("AIOptimizationEngine: No proposals generated")
        
        results["passed"].append("AIOptimizationEngine: Proposal generation")
        return True
    except Exception as e:
        console.print(f"❌ AIOptimizationEngine failed: {e}")
        import traceback
        traceback.print_exc()
        results["failed"].append(f"AIOptimizationEngine: {e}")
        return False

def test_io_scheduler():
    """Test 5: IOSchedulerOptimizer"""
    test_section("IOSchedulerOptimizer")
    
    try:
        from modules.optimizer import IOSchedulerOptimizer, HardwareDetector
        hw = HardwareDetector()
        io_opt = IOSchedulerOptimizer(hw)
        
        # Test device detection
        devices = io_opt.detect_block_devices()
        console.print(f"✅ Detected {len(devices)} block devices")
        
        for dev in devices:
            scheduler = io_opt.get_current_scheduler(dev['name'])
            optimal = io_opt.get_optimal_scheduler(dev['category'])
            console.print(f"  - {dev['name']}: {dev['category']} (current: {scheduler}, optimal: {optimal})")
        
        results["passed"].append("IOSchedulerOptimizer: Device detection")
        return True
    except Exception as e:
        console.print(f"❌ IOSchedulerOptimizer failed: {e}")
        import traceback
        traceback.print_exc()
        results["failed"].append(f"IOSchedulerOptimizer: {e}")
        return False

def test_transaction_manager():
    """Test 6: TransactionManager"""
    test_section("TransactionManager")
    
    try:
        from modules.optimizer import TransactionManager
        
        # Note: This requires root to write files
        console.print("⚠️  TransactionManager requires root for file operations")
        console.print("✅ Import successful")
        results["warnings"].append("TransactionManager: Requires root for full testing")
        results["passed"].append("TransactionManager: Import and structure")
        return True
    except Exception as e:
        console.print(f"❌ TransactionManager failed: {e}")
        results["failed"].append(f"TransactionManager: {e}")
        return False

def test_backup_manager():
    """Test 7: BackupManager"""
    test_section("BackupManager")
    
    try:
        from modules.optimizer import OptimizationBackup
        
        console.print("⚠️  OptimizationBackup requires root for file operations")
        console.print("✅ Import successful")
        results["warnings"].append("OptimizationBackup: Requires root for full testing")
        results["passed"].append("OptimizationBackup: Import and structure")
        return True
    except Exception as e:
        console.print(f"❌ OptimizationBackup failed: {e}")
        results["failed"].append(f"OptimizationBackup: {e}")
        return False

def test_facade():
    """Test 8: FedoraOptimizer Facade"""
    test_section("FedoraOptimizer Facade")
    
    try:
        from modules.optimizer import FedoraOptimizer
        opt = FedoraOptimizer()
        
        # Test system DNA
        dna = opt.get_system_dna()
        console.print(f"✅ System DNA generated ({len(dna)} entries)")
        
        # Test audit (may take time)
        console.print("Running deep system audit...")
        scores = opt.full_audit()
        console.print(f"✅ Audit completed")
        console.print(f"  - Categories audited: {len(scores)}")
        
        results["passed"].append("FedoraOptimizer: Facade orchestration")
        return True
    except Exception as e:
        console.print(f"❌ FedoraOptimizer Facade failed: {e}")
        import traceback
        traceback.print_exc()
        results["failed"].append(f"FedoraOptimizer: {e}")
        return False

def test_gaming_optimizer():
    """Test 9: GamingOptimizer"""
    test_section("GamingOptimizer")
    
    try:
        from modules.gaming import GamingOptimizer
        from modules.optimizer import HardwareDetector
        hw = HardwareDetector()
        gaming = GamingOptimizer(hw)
        
        console.print("✅ GamingOptimizer initialized")
        results["passed"].append("GamingOptimizer: Initialization")
        return True
    except Exception as e:
        console.print(f"❌ GamingOptimizer failed: {e}")
        import traceback
        traceback.print_exc()
        results["failed"].append(f"GamingOptimizer: {e}")
        return False

def print_summary():
    """Print test summary"""
    console.print(f"\n[bold]{'='*60}[/]")
    console.print(f"[bold]TEST SUMMARY[/]")
    console.print(f"[bold]{'='*60}[/]\n")
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")
    table.add_column("Percentage", justify="right")
    
    total = len(results["passed"]) + len(results["failed"])
    pass_pct = (len(results["passed"]) / total * 100) if total > 0 else 0
    
    table.add_row("[green]✅ Passed[/]", str(len(results["passed"])), f"{pass_pct:.1f}%")
    table.add_row("[red]❌ Failed[/]", str(len(results["failed"])), f"{100-pass_pct:.1f}%")
    table.add_row("[yellow]⚠️  Warnings[/]", str(len(results["warnings"])), "-")
    
    console.print(table)
    
    if results["failed"]:
        console.print("\n[bold red]Failed Tests:[/]")
        for fail in results["failed"]:
            console.print(f"  • {fail}")
    
    if results["warnings"]:
        console.print("\n[bold yellow]Warnings:[/]")
        for warn in results["warnings"]:
            console.print(f"  • {warn}")
    
    return len(results["failed"]) == 0

def main():
    console.print("[bold]FedoraOptimizer - Comprehensive Functionality Test[/]")
    console.print("[dim]Running all module tests...[/]\n")
    
    # Run all tests
    test_imports()
    test_hardware_detector()
    test_sysctl_optimizer()
    test_ai_engine()
    test_io_scheduler()
    test_transaction_manager()
    test_backup_manager()
    test_facade()
    test_gaming_optimizer()
    
    # Print summary
    success = print_summary()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
