"""
User Management Module
Handles user CRUD operations with security
"""

from typing import List, Dict, Optional
from datetime import datetime

from data_manager_v2 import DataManager
from config import DataPaths
from security import PasswordHasher, InputValidator
from logger import logger, audit_logger, error_handler
from validators import InputValidator as Validator


class UserManager(DataManager):
    """User management with secure password storage"""

    DEFAULT_ADMIN = {
        "username": "admin",
        "password_hash": "",  # Will be hashed on first load
        "role": "Admin",
        "name": "Administrator",
        "email": "",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "last_login": None,
        "is_active": True
    }

    def __init__(self):
        super().__init__(DataPaths.USERS_FILE, default_data=[])
        self.users = self._load_data()
        self._migrate_passwords()
        self._ensure_admin_exists()

    def _migrate_passwords(self):
        """Migrate plain text passwords to hashed passwords"""
        modified = False

        for user in self.users:
            # If user has plain text password (old format)
            if 'password' in user and 'password_hash' not in user:
                plain_password = user['password']
                user['password_hash'] = PasswordHasher.hash_password(plain_password)
                del user['password']
                modified = True
                logger.info(f"Migrated password for user: {user['username']}")

            # Ensure required fields
            if 'is_active' not in user:
                user['is_active'] = True
                modified = True

            if 'created_at' not in user:
                user['created_at'] = datetime.now().strftime("%Y-%m-%d")
                modified = True

        if modified:
            self._save_data(self.users)

    def _ensure_admin_exists(self):
        """Ensure default admin user exists"""
        admin_exists = any(u['username'] == 'admin' for u in self.users)

        if not admin_exists:
            admin = self.DEFAULT_ADMIN.copy()
            admin['password_hash'] = PasswordHasher.hash_password('123')

            self.users.append(admin)
            self._save_data(self.users)

            logger.info("Created default admin user")

    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return next((u for u in self.users if u['username'] == username), None)

    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username and password"""
        try:
            user = self.get_user(username)

            if not user:
                logger.warning(f"Authentication failed: User not found - {username}")
                return None

            if not user.get('is_active', True):
                logger.warning(f"Authentication failed: User inactive - {username}")
                return None

            # Verify password
            if PasswordHasher.verify_password(password, user['password_hash']):
                # Update last login
                user['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_data(self.users)

                audit_logger.log_security_event(
                    event_type='login_success',
                    username=username
                )

                logger.info(f"User authenticated: {username}")
                return user
            else:
                audit_logger.log_security_event(
                    event_type='login_failed',
                    username=username,
                    details={'reason': 'invalid_password'}
                )

                logger.warning(f"Authentication failed: Invalid password - {username}")
                return None

        except Exception as e:
            error_handler.handle_exception(e, context="authenticate")
            return None

    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        name: str,
        email: str = ""
    ) -> bool:
        """Create new user with validation"""
        try:
            # Validate username
            is_valid, error = Validator.validate_username(username)
            if not is_valid:
                logger.warning(f"Invalid username: {error}")
                return False

            # Check if user exists
            if self.get_user(username):
                logger.warning(f"User already exists: {username}")
                return False

            # Validate email if provided
            if email and not InputValidator.validate_email(email):
                logger.warning(f"Invalid email: {email}")
                return False

            # Validate role
            valid_roles = ["Admin", "Manager", "User", "Viewer"]
            if role not in valid_roles:
                logger.warning(f"Invalid role: {role}")
                return False

            # Hash password
            password_hash = PasswordHasher.hash_password(password)

            # Create user
            new_user = {
                "username": username,
                "password_hash": password_hash,
                "role": role,
                "name": name,
                "email": email,
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "last_login": None,
                "is_active": True
            }

            self.users.append(new_user)
            self._save_data(self.users)

            audit_logger.log_user_action(
                username='system',
                action='user_created',
                details={'new_user': username, 'role': role}
            )

            logger.info(f"Created new user: {username}")
            return True

        except Exception as e:
            error_handler.handle_exception(e, context="create_user")
            return False

    def update_user(self, username: str, update_data: Dict) -> bool:
        """Update user information"""
        try:
            user = self.get_user(username)

            if not user:
                logger.warning(f"User not found: {username}")
                return False

            # Don't allow updating username or password through this method
            if 'username' in update_data:
                del update_data['username']

            if 'password' in update_data:
                del update_data['password']

            # Validate email if being updated
            if 'email' in update_data and update_data['email']:
                if not InputValidator.validate_email(update_data['email']):
                    logger.warning(f"Invalid email: {update_data['email']}")
                    return False

            # Apply updates
            user.update(update_data)
            self._save_data(self.users)

            audit_logger.log_user_action(
                username='system',
                action='user_updated',
                details={'username': username, 'updates': list(update_data.keys())}
            )

            logger.info(f"Updated user: {username}")
            return True

        except Exception as e:
            error_handler.handle_exception(e, context="update_user")
            return False

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.get_user(username)

            if not user:
                return False

            # Verify old password
            if not PasswordHasher.verify_password(old_password, user['password_hash']):
                logger.warning(f"Password change failed: Invalid old password - {username}")
                return False

            # Hash new password
            user['password_hash'] = PasswordHasher.hash_password(new_password)
            self._save_data(self.users)

            audit_logger.log_security_event(
                event_type='password_changed',
                username=username
            )

            logger.info(f"Password changed for user: {username}")
            return True

        except Exception as e:
            error_handler.handle_exception(e, context="change_password")
            return False

    def delete_user(self, username: str) -> bool:
        """Delete user (cannot delete admin)"""
        try:
            if username == 'admin':
                logger.warning("Cannot delete admin user")
                return False

            original_count = len(self.users)
            self.users = [u for u in self.users if u['username'] != username]

            if len(self.users) < original_count:
                self._save_data(self.users)

                audit_logger.log_user_action(
                    username='system',
                    action='user_deleted',
                    details={'username': username}
                )

                logger.info(f"Deleted user: {username}")
                return True

            return False

        except Exception as e:
            error_handler.handle_exception(e, context="delete_user")
            return False

    def deactivate_user(self, username: str) -> bool:
        """Deactivate user account"""
        return self.update_user(username, {'is_active': False})

    def activate_user(self, username: str) -> bool:
        """Activate user account"""
        return self.update_user(username, {'is_active': True})

    def get_all_users(self) -> List[Dict]:
        """Get all users (excluding password hashes)"""
        return [
            {k: v for k, v in user.items() if k != 'password_hash'}
            for user in self.users
        ]


# Singleton instance
_user_manager = None


def get_user_manager() -> UserManager:
    """Get singleton UserManager instance"""
    global _user_manager

    if _user_manager is None:
        _user_manager = UserManager()

    return _user_manager
