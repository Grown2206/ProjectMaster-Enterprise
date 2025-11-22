"""
Data Validators Module
Validation functions for business logic
"""

from typing import Optional, Tuple, Any, Dict
from datetime import datetime
import re


class ProjectValidator:
    """Validate project data"""

    @staticmethod
    def validate_title(title: str) -> Tuple[bool, Optional[str]]:
        """Validate project title"""
        if not title or not title.strip():
            return False, "Titel darf nicht leer sein"

        if len(title) > 200:
            return False, "Titel darf maximal 200 Zeichen lang sein"

        return True, None

    @staticmethod
    def validate_category(category: str) -> Tuple[bool, Optional[str]]:
        """Validate project category"""
        valid_categories = ["IT", "Marketing", "HR", "R&D", "Privat", "Produktion", "Vertrieb", "Finanzen"]

        if category not in valid_categories:
            return False, f"Ungültige Kategorie. Erlaubt: {', '.join(valid_categories)}"

        return True, None

    @staticmethod
    def validate_priority(priority: str) -> Tuple[bool, Optional[str]]:
        """Validate project priority"""
        valid_priorities = ["Low", "Med", "High", "Critical"]

        if priority not in valid_priorities:
            return False, f"Ungültige Priorität. Erlaubt: {', '.join(valid_priorities)}"

        return True, None

    @staticmethod
    def validate_status(status: str) -> Tuple[bool, Optional[str]]:
        """Validate project status"""
        valid_statuses = ["Idee", "Planung", "In Arbeit", "Review", "Abgeschlossen", "Pausiert", "Abgebrochen"]

        if status not in valid_statuses:
            return False, f"Ungültiger Status. Erlaubt: {', '.join(valid_statuses)}"

        return True, None

    @staticmethod
    def validate_progress(progress: int) -> Tuple[bool, Optional[str]]:
        """Validate project progress"""
        if not isinstance(progress, int):
            return False, "Fortschritt muss eine Ganzzahl sein"

        if progress < 0 or progress > 100:
            return False, "Fortschritt muss zwischen 0 und 100 liegen"

        return True, None

    @staticmethod
    def validate_budget(budget: float) -> Tuple[bool, Optional[str]]:
        """Validate budget amount"""
        if not isinstance(budget, (int, float)):
            return False, "Budget muss eine Zahl sein"

        if budget < 0:
            return False, "Budget darf nicht negativ sein"

        if budget > 1_000_000_000:  # 1 Billion
            return False, "Budget ist unrealistisch hoch"

        return True, None


class TaskValidator:
    """Validate task data"""

    @staticmethod
    def validate_task_text(text: str) -> Tuple[bool, Optional[str]]:
        """Validate task text"""
        if not text or not text.strip():
            return False, "Aufgabentext darf nicht leer sein"

        if len(text) > 500:
            return False, "Aufgabentext darf maximal 500 Zeichen lang sein"

        return True, None

    @staticmethod
    def validate_task_status(status: str) -> Tuple[bool, Optional[str]]:
        """Validate task status"""
        valid_statuses = ["To Do", "In Progress", "Done", "Blocked"]

        if status not in valid_statuses:
            return False, f"Ungültiger Status. Erlaubt: {', '.join(valid_statuses)}"

        return True, None


class DateValidator:
    """Validate dates"""

    @staticmethod
    def validate_date_string(date_str: str) -> Tuple[bool, Optional[str]]:
        """Validate date string format (YYYY-MM-DD)"""
        if not date_str:
            return True, None  # Empty date is allowed

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True, None
        except ValueError:
            return False, "Datum muss im Format YYYY-MM-DD sein"

    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
        """Validate that end date is after start date"""
        if not start_date or not end_date:
            return True, None

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            if end < start:
                return False, "Enddatum muss nach Startdatum liegen"

            return True, None
        except ValueError:
            return False, "Ungültiges Datumsformat"


class FileValidator:
    """Validate file uploads"""

    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    ALLOWED_DOC_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.md', '.csv'}

    @staticmethod
    def validate_image(filename: str, file_size: int, max_size_mb: int = 10) -> Tuple[bool, Optional[str]]:
        """Validate image file"""
        # Check extension
        ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        if ext not in FileValidator.ALLOWED_IMAGE_EXTENSIONS:
            return False, f"Ungültiges Bildformat. Erlaubt: {', '.join(FileValidator.ALLOWED_IMAGE_EXTENSIONS)}"

        # Check size
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f"Datei ist zu groß. Maximum: {max_size_mb}MB"

        return True, None

    @staticmethod
    def validate_document(filename: str, file_size: int, max_size_mb: int = 20) -> Tuple[bool, Optional[str]]:
        """Validate document file"""
        # Check extension
        ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        if ext not in FileValidator.ALLOWED_DOC_EXTENSIONS:
            return False, f"Ungültiges Dokumentformat. Erlaubt: {', '.join(FileValidator.ALLOWED_DOC_EXTENSIONS)}"

        # Check size
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f"Datei ist zu groß. Maximum: {max_size_mb}MB"

        return True, None

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]

        # Remove dangerous characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')

        return filename


class ExperimentValidator:
    """Validate experiment data"""

    @staticmethod
    def validate_experiment_name(name: str) -> Tuple[bool, Optional[str]]:
        """Validate experiment name"""
        if not name or not name.strip():
            return False, "Versuchsname darf nicht leer sein"

        if len(name) > 200:
            return False, "Versuchsname darf maximal 200 Zeichen lang sein"

        return True, None

    @staticmethod
    def validate_sample_name(name: str) -> Tuple[bool, Optional[str]]:
        """Validate sample/specimen name"""
        if not name or not name.strip():
            return False, "Muster-Name darf nicht leer sein"

        if len(name) > 100:
            return False, "Muster-Name darf maximal 100 Zeichen lang sein"

        return True, None


class BudgetValidator:
    """Validate budget and financial data"""

    @staticmethod
    def validate_expense(title: str, amount: float, category: str) -> Tuple[bool, Optional[str]]:
        """Validate expense entry"""
        if not title or not title.strip():
            return False, "Ausgaben-Titel darf nicht leer sein"

        if not isinstance(amount, (int, float)):
            return False, "Betrag muss eine Zahl sein"

        if amount <= 0:
            return False, "Betrag muss positiv sein"

        valid_categories = ["Personal", "Ops", "Marketing", "Equipment", "Services", "Travel", "Other"]
        if category not in valid_categories:
            return False, f"Ungültige Kategorie. Erlaubt: {', '.join(valid_categories)}"

        return True, None
