"""
Logging Module
Centralized logging configuration for the application
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from config import Config


class Logger:
    """Application logger with file and console handlers"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not Logger._initialized:
            self.setup_logging()
            Logger._initialized = True

    def setup_logging(self):
        """Configure logging with file and console handlers"""
        # Ensure log directory exists
        Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger('ProjectMaster')
        self.logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)

        # File handler with rotation
        file_handler = RotatingFileHandler(
            Config.LOG_FILE,
            maxBytes=Config.LOG_MAX_SIZE_MB * 1024 * 1024,
            backupCount=Config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)

        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        self.logger.info("=" * 50)
        self.logger.info(f"{Config.APP_NAME} v{Config.APP_VERSION} Started")
        self.logger.info(f"Environment: {Config.APP_ENV}")
        self.logger.info("=" * 50)

    def get_logger(self):
        """Get the configured logger instance"""
        return self.logger


# Create singleton logger instance
_logger_instance = Logger()
logger = _logger_instance.get_logger()


# Convenience functions
def log_info(message: str, **kwargs):
    """Log info message"""
    logger.info(message, extra=kwargs)


def log_warning(message: str, **kwargs):
    """Log warning message"""
    logger.warning(message, extra=kwargs)


def log_error(message: str, exc_info=False, **kwargs):
    """Log error message"""
    logger.error(message, exc_info=exc_info, extra=kwargs)


def log_debug(message: str, **kwargs):
    """Log debug message"""
    logger.debug(message, extra=kwargs)


def log_critical(message: str, exc_info=True, **kwargs):
    """Log critical message"""
    logger.critical(message, exc_info=exc_info, extra=kwargs)


class AuditLogger:
    """Audit logger for tracking important business events"""

    @staticmethod
    def log_user_action(username: str, action: str, details: dict = None):
        """Log user action for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'action': action,
            'details': details or {}
        }
        logger.info(f"AUDIT: {action}", extra=log_entry)

    @staticmethod
    def log_project_change(username: str, project_id: str, action: str, details: dict = None):
        """Log project modification"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'username': username,
            'project_id': project_id,
            'action': action,
            'details': details or {}
        }
        logger.info(f"AUDIT[PROJECT]: {action}", extra=log_entry)

    @staticmethod
    def log_security_event(event_type: str, username: str = None, details: dict = None):
        """Log security-related event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'username': username,
            'details': details or {}
        }
        logger.warning(f"SECURITY: {event_type}", extra=log_entry)


class ErrorHandler:
    """Centralized error handling"""

    @staticmethod
    def handle_exception(error: Exception, context: str = "", user_message: str = None):
        """
        Handle exception with logging

        Args:
            error: The exception that occurred
            context: Context information about where the error occurred
            user_message: Optional user-friendly error message

        Returns:
            User-friendly error message
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        log_error(error_msg, exc_info=True)

        if user_message:
            return user_message
        else:
            if Config.is_production():
                return "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut."
            else:
                return f"Fehler: {error_msg}"

    @staticmethod
    def log_validation_error(field: str, error: str, username: str = None):
        """Log validation error"""
        log_warning(f"Validation error in {field}: {error}", extra={'username': username})


# Export audit logger instance
audit_logger = AuditLogger()
error_handler = ErrorHandler()
