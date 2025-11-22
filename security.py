"""
Security Module
Handles password hashing, validation, and security utilities
"""

import re
import bcrypt
import secrets
from typing import Optional, Tuple
from datetime import datetime, timedelta
from config import Config


class PasswordHasher:
    """Secure password hashing using bcrypt"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against its hash

        Args:
            password: Plain text password to verify
            hashed: Hashed password to check against

        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False


class PasswordValidator:
    """Validate password strength based on configuration"""

    @staticmethod
    def validate(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password against security requirements

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < Config.PASSWORD_MIN_LENGTH:
            return False, f"Passwort muss mindestens {Config.PASSWORD_MIN_LENGTH} Zeichen lang sein"

        if Config.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Passwort muss mindestens einen Großbuchstaben enthalten"

        if Config.PASSWORD_REQUIRE_NUMBER and not re.search(r'\d', password):
            return False, "Passwort muss mindestens eine Zahl enthalten"

        if Config.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Passwort muss mindestens ein Sonderzeichen enthalten"

        return True, None

    @staticmethod
    def get_strength(password: str) -> str:
        """
        Calculate password strength

        Args:
            password: Password to evaluate

        Returns:
            Strength rating: 'Schwach', 'Mittel', 'Stark'
        """
        score = 0

        # Length
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1

        # Complexity
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1

        if score <= 3:
            return "Schwach"
        elif score <= 5:
            return "Mittel"
        else:
            return "Stark"


class InputValidator:
    """Validate and sanitize user inputs"""

    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """
        Sanitize string input

        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not text:
            return ""

        # Remove leading/trailing whitespace
        text = text.strip()

        # Limit length
        text = text[:max_length]

        # Remove null bytes
        text = text.replace('\x00', '')

        return text

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format

        Args:
            email: Email address to validate

        Returns:
            True if valid email format
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, Optional[str]]:
        """
        Validate username

        Args:
            username: Username to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username or len(username) < 3:
            return False, "Benutzername muss mindestens 3 Zeichen lang sein"

        if len(username) > 30:
            return False, "Benutzername darf maximal 30 Zeichen lang sein"

        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Benutzername darf nur Buchstaben, Zahlen, _ und - enthalten"

        return True, None

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format

        Args:
            url: URL to validate

        Returns:
            True if valid URL format
        """
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))


class SessionManager:
    """Manage user sessions and login attempts"""

    def __init__(self):
        self.login_attempts = {}  # {username: [(timestamp, success), ...]}
        self.locked_accounts = {}  # {username: lockout_until}

    def record_login_attempt(self, username: str, success: bool):
        """Record a login attempt"""
        if username not in self.login_attempts:
            self.login_attempts[username] = []

        self.login_attempts[username].append({
            'timestamp': datetime.now(),
            'success': success
        })

        # Clean old attempts (older than 1 hour)
        cutoff = datetime.now() - timedelta(hours=1)
        self.login_attempts[username] = [
            attempt for attempt in self.login_attempts[username]
            if attempt['timestamp'] > cutoff
        ]

        # Check if account should be locked
        if not success:
            recent_failures = [
                a for a in self.login_attempts[username]
                if not a['success'] and a['timestamp'] > datetime.now() - timedelta(minutes=15)
            ]

            if len(recent_failures) >= Config.MAX_LOGIN_ATTEMPTS:
                self.locked_accounts[username] = datetime.now() + timedelta(
                    minutes=Config.LOCKOUT_DURATION_MINUTES
                )

    def is_account_locked(self, username: str) -> Tuple[bool, Optional[datetime]]:
        """
        Check if account is locked

        Returns:
            Tuple of (is_locked, lockout_until)
        """
        if username in self.locked_accounts:
            lockout_until = self.locked_accounts[username]
            if datetime.now() < lockout_until:
                return True, lockout_until
            else:
                # Lockout expired
                del self.locked_accounts[username]
                return False, None

        return False, None

    def unlock_account(self, username: str):
        """Manually unlock an account"""
        if username in self.locked_accounts:
            del self.locked_accounts[username]
        if username in self.login_attempts:
            del self.login_attempts[username]


class TokenGenerator:
    """Generate secure random tokens"""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_api_key() -> str:
        """Generate an API key"""
        return f"pm_{secrets.token_urlsafe(32)}"


# Singleton session manager
session_manager = SessionManager()
