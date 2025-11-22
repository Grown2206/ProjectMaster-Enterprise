"""
Configuration Management Module
Handles all application settings and environment variables
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class"""

    # Base paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"

    # Application
    APP_NAME = os.getenv("APP_NAME", "ProjectMaster Enterprise")
    APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
    APP_ENV = os.getenv("APP_ENV", "development")

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")

    # Database
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "json")
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR))
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(DATA_DIR / "projectmaster.db"))

    # File Storage
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
    IMAGE_DIR = Path(os.getenv("IMAGE_DIR", str(BASE_DIR / "project_images")))
    DOC_DIR = Path(os.getenv("DOC_DIR", str(BASE_DIR / "project_docs")))
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

    # Session
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = Path(os.getenv("LOG_FILE", str(LOGS_DIR / "app.log")))
    LOG_MAX_SIZE_MB = int(os.getenv("LOG_MAX_SIZE_MB", "10"))
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    # Features
    ENABLE_AI_ASSISTANT = os.getenv("ENABLE_AI_ASSISTANT", "true").lower() == "true"
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"
    ENABLE_BACKUP = os.getenv("ENABLE_BACKUP", "true").lower() == "true"
    BACKUP_INTERVAL_HOURS = int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))

    # Email
    SMTP_SERVER = os.getenv("SMTP_SERVER", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "noreply@projectmaster.com")

    # External APIs
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    # Performance
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))

    # Security Settings
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    PASSWORD_REQUIRE_SPECIAL = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
    PASSWORD_REQUIRE_NUMBER = os.getenv("PASSWORD_REQUIRE_NUMBER", "true").lower() == "true"
    PASSWORD_REQUIRE_UPPERCASE = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.DATA_DIR,
            cls.LOGS_DIR,
            cls.UPLOAD_DIR,
            cls.IMAGE_DIR,
            cls.DOC_DIR,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.APP_ENV.lower() == "production"

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.APP_ENV.lower() == "development"

    @classmethod
    def validate_config(cls) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []

        if cls.is_production() and cls.SECRET_KEY == "dev-secret-key-change-in-production":
            errors.append("SECRET_KEY must be changed in production")

        if cls.ENABLE_EMAIL_NOTIFICATIONS:
            if not cls.SMTP_SERVER:
                errors.append("SMTP_SERVER is required when email notifications are enabled")
            if not cls.SMTP_USERNAME:
                errors.append("SMTP_USERNAME is required when email notifications are enabled")

        return errors


# File paths for data storage
class DataPaths:
    """Data file paths configuration"""

    PROJECTS_FILE = Config.DATA_DIR / "projects_data.json"
    USERS_FILE = Config.DATA_DIR / "users_data.json"
    EXPERIMENTS_FILE = Config.DATA_DIR / "experiments_data.json"
    BACKUP_DIR = Config.DATA_DIR / "backups"

    @classmethod
    def ensure_data_files(cls):
        """Ensure data directory and backup directory exist"""
        Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# Initialize configuration on import
Config.ensure_directories()
DataPaths.ensure_data_files()

# Validate configuration
config_errors = Config.validate_config()
if config_errors:
    print("⚠️  Configuration Warnings:")
    for error in config_errors:
        print(f"  - {error}")
