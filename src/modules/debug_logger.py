"""
Debug Logger - Chrome DevTools-like error monitoring sistem
Real-time hata yakalama ve loglama
"""
import logging
import traceback
import functools
from datetime import datetime
from pathlib import Path


# Log file path
LOG_FILE = Path(__file__).parent.parent.parent / "debug.log"

# Configure logger
logger = logging.getLogger("FedoraOptimizerDebug")
logger.setLevel(logging.DEBUG)

# File handler with detailed formatting
file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Detailed formatter
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(funcName)-20s | %(message)s',
    datefmt='%H:%M:%S'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Also print to console for immediate feedback
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Only errors to console
logger.addHandler(console_handler)


def log_errors(func):
    """
    Decorator to catch and log all errors from functions.
    Chrome DevTools benzeri error catching.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.info(f"🟢 BAŞLADI: {func_name}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"✅ BAŞARILI: {func_name}")
            return result
            
        except Exception as e:
            # Detailed error logging
            logger.error(f"❌ HATA: {func_name}")
            logger.error(f"   Error Type: {type(e).__name__}")
            logger.error(f"   Error Message: {str(e)}")
            logger.error(f"   Stack Trace:")
            
            # Full stack trace
            for line in traceback.format_exc().split('\n'):
                if line.strip():
                    logger.error(f"   {line}")
            
            # Re-raise to show in TUI too
            raise
    
    return wrapper


def log_menu_action(menu_number, menu_name):
    """Log menu selection"""
    logger.info(f"")
    logger.info(f"{'='*60}")
    logger.info(f"📌 MENÜ SEÇİMİ: #{menu_number} - {menu_name}")
    logger.info(f"{'='*60}")


def log_operation(operation_name, status="START"):
    """Log operation start/end"""
    if status == "START":
        logger.info(f"🔵 İŞLEM BAŞLADI: {operation_name}")
    elif status == "SUCCESS":
        logger.info(f"✅ İŞLEM BAŞARILI: {operation_name}")
    elif status == "ERROR":
        logger.error(f"❌ İŞLEM BAŞARISIZ: {operation_name}")


def log_debug(message):
    """Debug message"""
    logger.debug(f"🔍 DEBUG: {message}")


def log_warning(message):
    """Warning message"""
    logger.warning(f"⚠️  WARNING: {message}")


# Initialize log file
logger.info(f"{'='*60}")
logger.info(f"FEDORA OPTIMIZER DEBUG LOG")
logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"Log File: {LOG_FILE}")
logger.info(f"{'='*60}")
logger.info("")
