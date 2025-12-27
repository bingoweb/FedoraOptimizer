"""
ULTRA-SENSITIVE Debug Logger with ML-Like Features
Production-grade error detection with pattern recognition
"""
import logging
import traceback
import functools
import sys
import os
import warnings
import inspect
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict
import threading
import time


# Log file paths
LOG_DIR = Path(__file__).parent.parent.parent
LOG_FILE = LOG_DIR / "debug.log"
ERROR_FILE = LOG_DIR / "errors_only.log"
ERROR_HISTORY_FILE = LOG_DIR / "error_history.json"
ANALYTICS_FILE = LOG_DIR / "debug_analytics.json"

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure main logger
logger = logging.getLogger("FedoraOptimizerDebug")
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

# File handler - ALL logs
file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Error-only handler
error_handler = logging.FileHandler(ERROR_FILE, mode='w', encoding='utf-8')
error_handler.setLevel(logging.ERROR)

# Ultra-detailed formatter
formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(filename)-20s:%(lineno)-4d | %(funcName)-30s | %(message)s',
    datefmt='%H:%M:%S'
)
file_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(error_handler)

# Console handler for CRITICAL errors only
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.CRITICAL)
console_formatter = logging.Formatter('💥 CRITICAL: %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

logger.propagate = False


# ============================================================================
# ML-LIKE ERROR ANALYSIS ENGINE
# ============================================================================

class ErrorPatternAnalyzer:
    """
    Machine Learning-like error pattern detection and analysis.
    Uses pattern matching, frequency analysis, and historical data.
    """
    
    def __init__(self):
        self.error_patterns = defaultdict(int)
        self.error_history = []
        self.known_fixes = self._load_known_fixes()
        self.session_errors = []
        self.error_clusters = defaultdict(list)
        
    def _load_known_fixes(self):
        """Load known error patterns and their fixes."""
        return {
            # Import errors
            "ModuleNotFoundError": {
                "pattern": r"No module named '(.+)'",
                "suggestion": "pip3 install {module} veya sudo pip3 install {module}",
                "severity": "high"
            },
            "ImportError": {
                "pattern": r"cannot import name '(.+)' from '(.+)'",
                "suggestion": "Check if {name} exists in {module}. May be renamed or removed.",
                "severity": "high"
            },
            # Syntax errors
            "SyntaxError": {
                "pattern": r"(.*)",
                "suggestion": "Kod syntax hatası. IDE'de dosyayı kontrol edin.",
                "severity": "critical"
            },
            "IndentationError": {
                "pattern": r"(.*)",
                "suggestion": "İndentasyon hatası. Spaces ve tabs karışmış olabilir.",
                "severity": "critical"
            },
            # Type errors
            "TypeError": {
                "pattern": r"'(.+)' object is not (.+)",
                "suggestion": "Tip uyuşmazlığı. Değişken tipini kontrol edin.",
                "severity": "medium"
            },
            "AttributeError": {
                "pattern": r"'(.+)' object has no attribute '(.+)'",
                "suggestion": "{obj_type} objesinde {attr} attribute yok. Yazım hatası veya eksik import.",
                "severity": "medium"
            },
            # Key/Index errors
            "KeyError": {
                "pattern": r"'(.+)'",
                "suggestion": "Dictionary'de '{key}' anahtarı yok. .get() kullanın veya key kontrolü yapın.",
                "severity": "medium"
            },
            "IndexError": {
                "pattern": r"(.*)",
                "suggestion": "Liste boyutu aşıldı. len() kontrolü ekleyin.",
                "severity": "medium"
            },
            # File errors
            "FileNotFoundError": {
                "pattern": r"No such file or directory: '(.+)'",
                "suggestion": "Dosya yolu yanlış veya dosya mevcut değil: {path}",
                "severity": "medium"
            },
            "PermissionError": {
                "pattern": r"(.*)",
                "suggestion": "Yetki hatası. sudo ile çalıştırın veya dosya izinlerini kontrol edin.",
                "severity": "high"
            },
            # Value errors
            "ValueError": {
                "pattern": r"(.*)",
                "suggestion": "Geçersiz değer. Girdi doğrulaması ekleyin.",
                "severity": "medium"
            },
            # Runtime errors
            "RuntimeError": {
                "pattern": r"(.*)",
                "suggestion": "Çalışma zamanı hatası. Detaylar için stack trace inceleyin.",
                "severity": "high"
            },
            # OS errors
            "OSError": {
                "pattern": r"(.*)",
                "suggestion": "İşletim sistemi hatası. Dosya/ağ/izin sorunları olabilir.",
                "severity": "high"
            }
        }
    
    def analyze_error(self, exc_type, exc_value, exc_traceback):
        """
        Analyze error and provide ML-like insights.
        """
        error_name = exc_type.__name__
        error_msg = str(exc_value)
        
        # Create error signature (hash for pattern matching)
        signature = self._create_error_signature(error_name, error_msg, exc_traceback)
        
        # Update pattern frequency
        self.error_patterns[signature] += 1
        
        # Record in history
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "type": error_name,
            "message": error_msg[:500],
            "signature": signature,
            "file": self._get_error_file(exc_traceback),
            "line": self._get_error_line(exc_traceback),
            "count": self.error_patterns[signature]
        }
        self.session_errors.append(error_record)
        self.error_clusters[error_name].append(error_record)
        
        # Get analysis
        analysis = {
            "signature": signature,
            "frequency": self.error_patterns[signature],
            "is_recurring": self.error_patterns[signature] > 1,
            "known_fix": self._get_known_fix(error_name, error_msg),
            "similar_errors": self._find_similar_errors(signature),
            "severity": self._calculate_severity(error_name, error_msg),
            "root_cause_hints": self._detect_root_cause(exc_traceback)
        }
        
        return analysis
    
    def _create_error_signature(self, error_name, error_msg, tb):
        """Create unique signature for error pattern."""
        # Normalize error message (remove variable values)
        normalized = re.sub(r"'[^']*'", "'X'", error_msg)
        normalized = re.sub(r'"[^"]*"', '"X"', normalized)
        normalized = re.sub(r'\d+', 'N', normalized)
        
        # Include location
        file_name = self._get_error_file(tb) or "unknown"
        
        signature_str = f"{error_name}:{normalized}:{file_name}"
        return hashlib.md5(signature_str.encode()).hexdigest()[:12]
    
    def _get_error_file(self, tb):
        """Get file where error occurred."""
        if tb is None:
            return None
        while tb.tb_next:
            tb = tb.tb_next
        return Path(tb.tb_frame.f_code.co_filename).name
    
    def _get_error_line(self, tb):
        """Get line number where error occurred."""
        if tb is None:
            return None
        while tb.tb_next:
            tb = tb.tb_next
        return tb.tb_lineno
    
    def _get_known_fix(self, error_name, error_msg):
        """Get known fix suggestion for error type."""
        if error_name in self.known_fixes:
            fix_info = self.known_fixes[error_name]
            suggestion = fix_info["suggestion"]
            
            # Extract variables from error message
            pattern = fix_info["pattern"]
            match = re.search(pattern, error_msg)
            if match:
                groups = match.groups()
                # Simple variable substitution
                if "{module}" in suggestion and groups:
                    suggestion = suggestion.replace("{module}", groups[0])
                if "{name}" in suggestion and len(groups) > 0:
                    suggestion = suggestion.replace("{name}", groups[0])
                if "{key}" in suggestion and groups:
                    suggestion = suggestion.replace("{key}", groups[0])
                if "{path}" in suggestion and groups:
                    suggestion = suggestion.replace("{path}", groups[0])
            
            return {
                "suggestion": suggestion,
                "severity": fix_info["severity"]
            }
        return None
    
    def _find_similar_errors(self, signature):
        """Find similar errors from history."""
        similar = []
        for error in self.session_errors:
            if error["signature"] == signature:
                similar.append(error)
        return similar[-5:]  # Last 5 similar
    
    def _calculate_severity(self, error_name, error_msg):
        """Calculate error severity score (0-10)."""
        base_severity = {
            "SyntaxError": 10,
            "IndentationError": 10,
            "ImportError": 9,
            "ModuleNotFoundError": 9,
            "PermissionError": 8,
            "FileNotFoundError": 7,
            "AttributeError": 6,
            "TypeError": 6,
            "KeyError": 5,
            "ValueError": 5,
            "IndexError": 5,
            "RuntimeError": 7,
            "OSError": 7
        }.get(error_name, 5)
        
        # Adjust based on frequency
        if self.error_patterns.get(error_name, 0) > 3:
            base_severity = min(10, base_severity + 1)
        
        return base_severity
    
    def _detect_root_cause(self, tb):
        """Try to detect root cause from traceback."""
        hints = []
        
        if tb is None:
            return hints
        
        # Analyze call stack
        frames = []
        current_tb = tb
        while current_tb:
            frame = current_tb.tb_frame
            frames.append({
                "file": frame.f_code.co_filename,
                "func": frame.f_code.co_name,
                "line": current_tb.tb_lineno
            })
            current_tb = current_tb.tb_next
        
        # Look for common patterns
        for frame in frames:
            if "__init__" in frame["func"]:
                hints.append("Hata initialization sırasında oluştu - constructor kontrol edin")
            if "import" in frame["file"].lower() or "init" in frame["file"]:
                hints.append("Import sırasında hata - circular import olabilir")
        
        # Check if error is in user code vs library
        user_frames = [f for f in frames if "site-packages" not in f["file"]]
        if user_frames:
            last_user_frame = user_frames[-1]
            hints.append(f"Son kullanıcı kodu: {Path(last_user_frame['file']).name}:{last_user_frame['line']}")
        
        return hints
    
    def get_session_summary(self):
        """Get summary of all errors in current session."""
        return {
            "total_errors": len(self.session_errors),
            "unique_errors": len(self.error_patterns),
            "error_types": dict(Counter(e["type"] for e in self.session_errors)),
            "most_common": Counter(e["signature"] for e in self.session_errors).most_common(5),
            "recurring_errors": [sig for sig, count in self.error_patterns.items() if count > 1]
        }


# Global analyzer instance
error_analyzer = ErrorPatternAnalyzer()


# ============================================================================
# WARNING CAPTURE SYSTEM
# ============================================================================

def warning_handler(message, category, filename, lineno, file=None, line=None):
    """Capture ALL Python warnings."""
    logger.warning(f"⚠️  PYTHON WARNING: {category.__name__}")
    logger.warning(f"   Message: {message}")
    logger.warning(f"   Location: {filename}:{lineno}")
    if line:
        logger.warning(f"   Code: {line.strip()}")


# Install warning handler
warnings.showwarning = warning_handler
warnings.simplefilter("always")


# ============================================================================
# EXCEPTION HOOK WITH ML ANALYSIS
# ============================================================================

def exception_hook(exc_type, exc_value, exc_traceback):
    """Catch uncaught exceptions with ML analysis."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # ML Analysis
    analysis = error_analyzer.analyze_error(exc_type, exc_value, exc_traceback)
    
    logger.critical("="*80)
    logger.critical("💥 UNCAUGHT EXCEPTION - CRITICAL FAILURE")
    logger.critical("="*80)
    logger.critical(f"Type: {exc_type.__module__}.{exc_type.__name__}")
    logger.critical(f"Message: {exc_value}")
    logger.critical("")
    
    # ML Insights
    logger.critical("🤖 ML ANALİZİ:")
    logger.critical(f"   Signature: {analysis['signature']}")
    logger.critical(f"   Severity: {analysis['severity']}/10")
    logger.critical(f"   Recurring: {'EVET (daha önce görüldü!)' if analysis['is_recurring'] else 'İlk kez'}")
    logger.critical(f"   Frequency: {analysis['frequency']} kez")
    
    if analysis['known_fix']:
        logger.critical("")
        logger.critical("💡 ÖNERİLEN ÇÖZÜM:")
        logger.critical(f"   {analysis['known_fix']['suggestion']}")
    
    if analysis['root_cause_hints']:
        logger.critical("")
        logger.critical("🔍 OLASI NEDEN:")
        for hint in analysis['root_cause_hints']:
            logger.critical(f"   • {hint}")
    
    logger.critical("")
    logger.critical("Full Traceback:")
    for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
        for l in line.split('\n'):
            if l.strip():
                logger.critical(l)
    logger.critical("="*80)


sys.excepthook = exception_hook


# ============================================================================
# PERFORMANCE TRACKING
# ============================================================================

class PerformanceTracker:
    """Track function performance with anomaly detection."""
    
    def __init__(self):
        self.timings = defaultdict(list)
        self.anomalies = []
    
    def record(self, func_name, duration):
        self.timings[func_name].append(duration)
        
        # Calculate statistics
        times = self.timings[func_name]
        avg = sum(times) / len(times)
        
        # Anomaly detection (>2x average or >1 second)
        if len(times) > 3 and duration > avg * 2:
            self.anomalies.append({
                "func": func_name,
                "duration": duration,
                "avg": avg,
                "ratio": duration / avg
            })
            logger.warning(f"🐌 PERFORMANCE ANOMALY: {func_name}")
            logger.warning(f"   Duration: {duration:.2f}s (avg: {avg:.2f}s)")
            logger.warning(f"   {duration/avg:.1f}x slower than average!")
        elif duration > 1.0:
            logger.warning(f"🐌 SLOW FUNCTION: {func_name} took {duration:.2f}s")
        elif duration > 5.0:
            logger.error(f"🐌🐌 VERY SLOW: {func_name} took {duration:.2f}s")


perf_tracker = PerformanceTracker()


# ============================================================================
# ENHANCED DECORATOR
# ============================================================================

def log_errors(func):
    """Ultra-sensitive decorator with ML-like error analysis."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name = func.__module__
        full_name = f"{module_name}.{func_name}"
        
        logger.info(f"{'='*80}")
        logger.info(f"🟢 FUNCTION ENTRY: {full_name}")
        
        # Log arguments (safely)
        try:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            for arg_name, arg_value in bound_args.arguments.items():
                try:
                    value_repr = repr(arg_value)[:200]
                    logger.debug(f"   arg '{arg_name}' = {value_repr}")
                except Exception:
                    logger.debug(f"   arg '{arg_name}' = <cannot repr>")
        except Exception:
            pass
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            perf_tracker.record(full_name, duration)
            
            logger.info(f"✅ FUNCTION SUCCESS: {full_name} ({duration:.3f}s)")
            logger.info(f"{'='*80}\n")
            
            return result
            
        except KeyboardInterrupt:
            duration = time.time() - start_time
            logger.warning(f"⚠️  INTERRUPTED: {full_name} (after {duration:.3f}s)")
            raise
            
        except Exception as e:
            duration = time.time() - start_time
            exc_type, exc_value, exc_traceback = sys.exc_info()
            
            # ML Analysis
            analysis = error_analyzer.analyze_error(exc_type, exc_value, exc_traceback)
            
            logger.error(f"{'='*80}")
            logger.error(f"❌ EXCEPTION in {full_name}")
            logger.error(f"{'='*80}")
            logger.error(f"Exception Type: {type(e).__module__}.{type(e).__name__}")
            logger.error(f"Exception Message: {str(e)}")
            logger.error(f"Duration before error: {duration:.3f}s")
            logger.error("")
            
            # ML Insights
            logger.error("🤖 ML ANALİZİ:")
            logger.error(f"   Severity: {analysis['severity']}/10")
            logger.error(f"   Recurring: {'EVET' if analysis['is_recurring'] else 'Hayır'}")
            
            if analysis['known_fix']:
                logger.error("")
                logger.error("💡 ÖNERİLEN ÇÖZÜM:")
                logger.error(f"   {analysis['known_fix']['suggestion']}")
            
            logger.error("")
            logger.error("Stack Trace:")
            logger.error(f"{'-'*80}")
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    logger.error(line)
            logger.error(f"{'-'*80}")
            
            # Local variables
            try:
                tb = exc_traceback
                frame = tb.tb_frame
                logger.error("")
                logger.error("Local Variables:")
                local_vars = list(frame.f_locals.items())[:10]
                for var_name, var_value in local_vars:
                    try:
                        value_repr = repr(var_value)[:100]
                        logger.error(f"   {var_name} = {value_repr}")
                    except Exception:
                        logger.error(f"   {var_name} = <cannot repr>")
            except Exception:
                pass
            
            logger.error(f"{'='*80}\n")
            raise
    
    return wrapper


# ============================================================================
# LOGGING HELPER FUNCTIONS
# ============================================================================

def log_menu_action(menu_number, menu_name):
    """Log menu selection."""
    logger.info("")
    logger.info(f"{'#'*80}")
    logger.info(f"📌 MENU SELECTION: #{menu_number} - {menu_name}")
    logger.info(f"   Timestamp: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
    logger.info(f"{'#'*80}")
    logger.info("")


def log_operation(operation_name, status="START", details=None):
    """Log operation with details."""
    icons = {
        "START": "🔵",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "INFO": "ℹ️"
    }
    icon = icons.get(status, "🔹")
    
    level_map = {
        "START": logging.INFO,
        "SUCCESS": logging.INFO,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO
    }
    level = level_map.get(status, logging.INFO)
    
    msg = f"{icon} OPERATION {status}: {operation_name}"
    if details:
        msg += f"\n   Details: {details}"
    
    logger.log(level, msg)


def log_debug(message, **context):
    """Debug with context."""
    logger.debug(f"🔍 {message}")
    for key, value in context.items():
        try:
            logger.debug(f"   {key}: {repr(value)[:150]}")
        except Exception:
            logger.debug(f"   {key}: <cannot repr>")


def log_warning(message, **context):
    """Warning with context."""
    logger.warning(f"⚠️  {message}")
    for key, value in context.items():
        try:
            logger.warning(f"   {key}: {repr(value)[:150]}")
        except Exception:
            logger.warning(f"   {key}: <cannot repr>")


def log_info(message):
    """Info message."""
    logger.info(f"ℹ️  {message}")


def log_critical(message):
    """Critical message."""
    logger.critical(f"💥 CRITICAL: {message}")


def get_error_summary():
    """Get error summary for display."""
    return error_analyzer.get_session_summary()


# ============================================================================
# INITIALIZATION
# ============================================================================

def init_log():
    """Initialize with system information."""
    logger.info(f"{'='*80}")
    logger.info(f"FEDORA OPTIMIZER - ML-ENHANCED DEBUG CONSOLE v3.0")
    logger.info(f"{'='*80}")
    logger.info(f"Session Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    logger.info(f"Log Files:")
    logger.info(f"   Full Log: {LOG_FILE}")
    logger.info(f"   Errors Only: {ERROR_FILE}")
    logger.info(f"")
    logger.info(f"Python: {sys.version.split()[0]}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"CWD: {os.getcwd()}")
    logger.info(f"")
    logger.info(f"🤖 ML FEATURES ENABLED:")
    logger.info(f"   • Error Pattern Detection")
    logger.info(f"   • Severity Calculation")
    logger.info(f"   • Known Fix Suggestions")
    logger.info(f"   • Root Cause Analysis")
    logger.info(f"   • Performance Anomaly Detection")
    logger.info(f"   • Recurring Error Tracking")
    logger.info(f"{'='*80}")
    logger.info("")


# Auto-initialize
init_log()
