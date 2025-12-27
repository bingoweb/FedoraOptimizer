# Changelog

All notable changes to Fedora Optimizer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.2] - 2025-12-27

### Added
- **Test Infrastructure**: Comprehensive pytest framework with 54+ tests
  - Created `tests/` directory with unit, integration, and fixtures
  - Added `MockHardwareDetector` for testing without real hardware
  - Implemented 4 test fixtures (nvme, gamer, laptop, server)
  - Created test files: test_sysctl_optimizer (11), test_hardware_detector (10), test_ai_engine (8), test_facade (5), test_security (20+)
  - Added `pytest.ini` configuration
  - Added GitHub Actions CI/CD workflow (`.github/workflows/tests.yml`)
  - Added comprehensive test documentation (`tests/README.md`)

- **Security Module**: Input validation and protection (`src/modules/optimizer/security.py`)
  - `validate_sysctl_param()` - Prevents command injection in parameter names
  - `validate_sysctl_value()` - Blocks shell metacharacters in values
  - `validate_file_path()` - Prevents path traversal attacks
  - `sanitize_string()` - Safe string cleaning with length limits
  - `write_secure_file()` - Enforces 0600 file permissions
  - `ensure_secure_directory()` - Enforces 0700 directory permissions
  - 20+ security tests covering all attack vectors

- **New Optimizer Modules**: Extracted from facade for better separation of concerns
  - `SystemProfiler` (175 lines) - System DNA, persona detection, scoring
  - `DNFOptimizer` (77 lines) - Package manager optimization
  - `BootOptimizer` (55 lines) - Boot time optimization

### Changed
- **Facade Refactoring**: Reduced `facade.py` from 622 to 130 lines (-79%)
  - Implemented delegation pattern to specialized modules
  - Kept `optimize_full_auto()` as main orchestration method
  - Maintained backward compatibility with TUI
  - Updated `__init__.py` to export new modules

### Fixed
- Command injection vulnerabilities in sysctl operations
- Path traversal vulnerabilities in file operations
- Insecure file permissions (644 → 600 for sensitive files)

### Security
- **CRITICAL**: All user inputs now validated before use
- **CRITICAL**: Command injection attempts blocked (`;`, `|`, `&&`, `` ` ``, `$()`)
- **CRITICAL**: Path traversal attacks prevented (`../`)
- **CRITICAL**: Secure file permissions enforced (0600/0700)

### Improved
- Code organization: Modular, focused responsibilities
- Testability: 54+ tests provide safety net for refactoring
- Maintainability: Smaller, focused modules easier to understand
- Security posture: High Risk → Protected
- Documentation: Comprehensive test guides and examples

## [0.3.1] - 2025-12-27

### Added
- `AIOptimizationEngine.analyze_io_scheduler()` - Analyzes I/O schedulers for all block devices with workload-aware recommendations
- `AIOptimizationEngine.analyze_network_only()` - Network-only parameter analysis with buffer size optimization  
- `FedoraOptimizer.analyze_usage_persona()` - Intelligent usage profile detection (Gamer/Developer/Server/General)
- `TransactionManager.reset_to_defaults()` - Complete system reset functionality with config file cleanup
- Comprehensive docstrings for 7 private analysis methods in `engine.py`
- Updated `docs/AI_MEMORY.md` with complete architecture documentation and development guidelines

### Fixed
- **Critical:** TUI Menu 3 (Full Auto) now works correctly with persona detection
- **Critical:** TUI Menu 5 (I/O Scheduler) now functional with device analysis
- **Critical:** TUI Menu 6 (Network Optimize) now works with network-only mode
- **Critical:** TUI Menu 7 (Kernel Tuning) improved with persona detection
- **Critical:** TUI Menu 8.3 (Reset to Defaults) now available
- Missing `encoding="utf-8"` in 15+ file operations across 5 modules
- AttributeError issues caused by missing method implementations

### Changed
- `io_scheduler.py`: Improved type hints from `list` to `List[Dict[str, str]]`
- `io_scheduler.py`: More specific exception handling using `(OSError, PermissionError)`
- `sysctl.py`: Removed redundant `_detect_disk_type()` method, now uses `hw.get_simple_disk_type()` directly

### Improved
- **TUI Functionality:** Increased from 60% to 100% working menu options
- **Code Quality:** Enhanced type safety and error handling
- **Documentation:** Comprehensive architecture and development documentation
- **Maintainability:** Reduced code duplication and improved clarity

## [0.3.0] - 2025-12-21

### Added
- Modular architecture with separate package structure in `src/modules/optimizer/`
- Transaction-based rollback system with UUID tracking
- Backup and restore functionality with snapshot management
- Individual optimizer modules: `hardware.py`, `engine.py`, `sysctl.py`, `io_scheduler.py`, `facade.py`

### Changed
- Split monolithic `optimizer.py` (2730 lines) into focused, modular components
- **Pylint Score:** Improved from ~6.0 to 9.21/10

### Improved
- Code organization and separation of concerns
- Testability and maintainability
- Development workflow

## [0.2.5] - 2025-12-20

### Added
- Hardware-aware AI tuning with form factor intelligence
- Form factor detection: Laptop vs Desktop vs Server
- CPU intelligence: Intel Hybrid (P+E cores), AMD Zen detection
- Laptop-specific optimizations (battery life tuning)
- Desktop-specific optimizations (performance tuning)

### Improved
- Smart parameter selection based on detected hardware
- Context-aware optimization recommendations

## [0.2.4] - 2025-12-19

### Added
- Smart profile management with automatic workload detection
- Profile categories: Gamer, Developer, Server, General
- Binary scanning for installed software (steam, docker, nginx, vscode)
- Profile-specific optimizations:
  - **Gamer:** `vm.max_map_count`, `kernel.sched_latency_ns`
  - **Developer:** `fs.inotify.max_user_watches`
  - **Server:** `net.core.somaxconn`

### Improved
- Intelligent optimization targeting
- User-specific workload recognition

## [0.2.3] - 2025-12-18

### Added
- Deep DNA reporting with 0-100 scoring system
- Category-based audit: CPU (25p), Memory (25p), Disk (25p), Network (15p), Kernel (10p)
- ASCII progress bars in TUI visualization
- Detailed category breakdowns with recommendations

### Improved
- User-friendly scoring visualization
- Actionable optimization suggestions

## [0.2.1] - 2025-12-17

### Added
- 2025 kernel technology support
- BBRv3 smart detection (bbr, bbr2, bbr3)
- PSI (Pressure Stall Information) monitoring from `/proc/pressure`
- sched_ext detection for Kernel 6.12+
- io_uring, BPF, cgroup v2 feature detection

### Improved
- Modern kernel feature utilization
- Real-time system stress monitoring

## [0.2.0] - 2025-12-15

### Added
- AI-driven optimization workflow: SCAN → ANALYZE → EXPLAIN → CONFIRM → APPLY
- Rich TUI with live updates
- Universal hardware detection system
- Proposal-based optimization system with explanations
- Transaction-based rollback mechanism

### Changed
- Complete rewrite with modern Python patterns
- Rich library for enhanced CLI experience

## [0.1.0] - 2025-12-10

### Added
- Initial release
- Basic optimization features
- DNF configuration
- Kernel parameter tuning
- I/O scheduler optimization

---

[0.3.1]: https://github.com/bingoweb/FedoraOptimizer/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/bingoweb/FedoraOptimizer/compare/v0.2.5...v0.3.0
[0.2.5]: https://github.com/bingoweb/FedoraOptimizer/compare/v0.2.4...v0.2.5
[0.2.4]: https://github.com/bingoweb/FedoraOptimizer/compare/v0.2.3...v0.2.4
[0.2.3]: https://github.com/bingoweb/FedoraOptimizer/compare/v0.2.1...v0.2.3
[0.2.1]: https://github.com/bingoweb/FedoraOptimizer/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/bingoweb/FedoraOptimizer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/bingoweb/FedoraOptimizer/releases/tag/v0.1.0
