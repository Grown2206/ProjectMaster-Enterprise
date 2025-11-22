"""
Data Manager Module v2.0
Enhanced project management with proper error handling, validation, and logging
"""

import json
import os
import uuid
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

from config import Config, DataPaths
from logger import logger, audit_logger, error_handler
from validators import (
    ProjectValidator, TaskValidator, DateValidator,
    ExperimentValidator, BudgetValidator
)
from security import InputValidator


class DataManager:
    """Base class for data persistence"""

    def __init__(self, file_path: Path, default_data: Any = None):
        self.file_path = file_path
        self.default_data = default_data if default_data is not None else []
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensure data file exists"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            self._save_data(self.default_data)
            logger.info(f"Created new data file: {self.file_path}")

    def _load_data(self) -> Any:
        """Load data from JSON file with error handling"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Loaded data from {self.file_path}")
                return data
        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error in {self.file_path}: {str(e)}"
            logger.error(error_msg)
            return self._restore_from_backup() or self.default_data
        except Exception as e:
            error_msg = f"Error loading data from {self.file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self.default_data

    def _save_data(self, data: Any):
        """Save data to JSON file with backup"""
        try:
            # Create backup if file exists
            if self.file_path.exists() and Config.ENABLE_BACKUP:
                self._create_backup()

            # Write data
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            logger.debug(f"Saved data to {self.file_path}")

        except Exception as e:
            error_msg = f"Error saving data to {self.file_path}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def _create_backup(self):
        """Create backup of current data file"""
        try:
            backup_dir = DataPaths.BACKUP_DIR
            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"{self.file_path.stem}_backup_{timestamp}.json"

            shutil.copy2(self.file_path, backup_file)
            logger.debug(f"Created backup: {backup_file}")

            # Clean old backups (keep last 10)
            self._clean_old_backups(backup_dir, keep=10)

        except Exception as e:
            logger.warning(f"Failed to create backup: {str(e)}")

    def _clean_old_backups(self, backup_dir: Path, keep: int = 10):
        """Remove old backup files"""
        try:
            backups = sorted(
                backup_dir.glob(f"{self.file_path.stem}_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            for backup in backups[keep:]:
                backup.unlink()
                logger.debug(f"Removed old backup: {backup}")

        except Exception as e:
            logger.warning(f"Failed to clean old backups: {str(e)}")

    def _restore_from_backup(self) -> Optional[Any]:
        """Restore data from most recent backup"""
        try:
            backup_dir = DataPaths.BACKUP_DIR

            backups = sorted(
                backup_dir.glob(f"{self.file_path.stem}_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            if backups:
                backup_file = backups[0]
                with open(backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Restored data from backup: {backup_file}")
                return data

        except Exception as e:
            logger.error(f"Failed to restore from backup: {str(e)}")

        return None


class ProjectManager(DataManager):
    """Enhanced Project Manager with validation and error handling"""

    def __init__(self):
        super().__init__(DataPaths.PROJECTS_FILE)
        self.projects = self._load_data()
        self._migrate_legacy_data()

        # User management
        self.users_file = Config.DATA_DIR / "users_data.json"
        self.users = self._load_users()

        # Experiments management
        self.experiments_file = Config.DATA_DIR / "experiments_data.json"
        self.experiments = self._load_experiments()

    def _load_users(self) -> List[Dict]:
        """Load users from JSON file"""
        try:
            if not self.users_file.exists():
                default_users = [
                    {
                        "username": "admin",
                        "password": "123",
                        "role": "Admin",
                        "name": "Administrator"
                    }
                ]
                self.users_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.users_file, 'w', encoding='utf-8') as f:
                    json.dump(default_users, f, indent=4)
                return default_users

            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading users: {str(e)}")
            return [{"username": "admin", "password": "123", "role": "Admin", "name": "Administrator"}]

    def _save_users(self):
        """Save users to JSON file"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving users: {str(e)}")

    def add_user(self, username: str, password: str, role: str, name: str) -> bool:
        """Add new user"""
        if any(u['username'] == username for u in self.users):
            return False

        self.users.append({
            "username": username,
            "password": password,
            "role": role,
            "name": name
        })
        self._save_users()
        audit_logger.log_user_action("system", f"User created: {username}", {"role": role, "name": name})
        return True

    def _load_experiments(self) -> List[Dict]:
        """Load experiments from JSON file"""
        try:
            if not self.experiments_file.exists():
                self.experiments_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.experiments_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=4)
                return []

            with open(self.experiments_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading experiments: {str(e)}")
            return []

    def save_experiments(self):
        """Save experiments to JSON file"""
        try:
            with open(self.experiments_file, 'w', encoding='utf-8') as f:
                json.dump(self.experiments, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving experiments: {str(e)}")

    def _migrate_legacy_data(self):
        """Migrate legacy project data to new format"""
        try:
            modified = False

            for project in self.projects:
                # Ensure all required fields exist
                required_fields = {
                    'images': [],
                    'risks': [],
                    'team': [],
                    'activity_log': [],
                    'tags': [],
                    'documents': [],
                    'decisions': [],
                    'bugs': [],
                    'stakeholders': [],
                    'meetings': [],
                    'secrets': [],
                    'okrs': [],
                    'retros': [],
                    'wiki_pages': [],
                    'backlog': [],
                    'test_cases': [],
                    'test_runs': [],
                    'automations': [],
                    'milestones': [],
                    'time_logs': [],
                }

                for field, default_value in required_fields.items():
                    if field not in project:
                        project[field] = default_value
                        modified = True

                # Ensure budget structure
                if 'budget' not in project:
                    project['budget'] = {
                        'total': 0.0,
                        'currency': 'EUR',
                        'expenses': []
                    }
                    modified = True

                # Ensure SWOT structure
                if 'swot' not in project:
                    project['swot'] = {
                        'strengths': [],
                        'weaknesses': [],
                        'opportunities': [],
                        'threats': []
                    }
                    modified = True

                # Ensure tasks have proper structure
                if 'tasks' not in project:
                    project['tasks'] = []

                for task in project.get('tasks', []):
                    if 'id' not in task:
                        task['id'] = str(uuid.uuid4())
                        modified = True

                    if 'status' not in task:
                        task['status'] = 'Done' if task.get('done') else 'To Do'
                        modified = True

                    if 'comments' not in task:
                        task['comments'] = []
                        modified = True

                    if 'assignee' not in task:
                        task['assignee'] = None
                        modified = True

            if modified:
                self._save_data(self.projects)
                logger.info("Migrated legacy project data")

        except Exception as e:
            logger.error(f"Error migrating legacy data: {str(e)}", exc_info=True)

    def save(self):
        """Save projects to file"""
        self._save_data(self.projects)

    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        return next((p for p in self.projects if p['id'] == project_id), None)

    def add_project(
        self,
        title: str,
        description: str,
        category: str,
        priority: str,
        deadline: Optional[str] = None,
        git_url: str = "",
        tags: List[str] = None,
        is_template: bool = False
    ) -> Optional[str]:
        """
        Add new project with validation

        Returns:
            Project ID if successful, None if validation fails
        """
        try:
            # Validate inputs
            is_valid, error = ProjectValidator.validate_title(title)
            if not is_valid:
                logger.warning(f"Invalid project title: {error}")
                return None

            is_valid, error = ProjectValidator.validate_category(category)
            if not is_valid:
                logger.warning(f"Invalid category: {error}")
                return None

            is_valid, error = ProjectValidator.validate_priority(priority)
            if not is_valid:
                logger.warning(f"Invalid priority: {error}")
                return None

            if deadline:
                is_valid, error = DateValidator.validate_date_string(deadline)
                if not is_valid:
                    logger.warning(f"Invalid deadline: {error}")
                    return None

            # Sanitize inputs
            title = InputValidator.sanitize_string(title, 200)
            description = InputValidator.sanitize_string(description, 5000)
            git_url = InputValidator.sanitize_string(git_url, 500)

            # Create project
            project_id = str(uuid.uuid4())

            new_project = {
                'id': project_id,
                'title': title,
                'description': description,
                'category': category,
                'priority': priority,
                'deadline': deadline,
                'status': 'Idee',
                'progress': 0,
                'images': [],
                'git_url': git_url,
                'tags': tags or [],
                'is_template': is_template,
                'is_archived': False,
                'is_deleted': False,
                'created_at': datetime.now().strftime("%Y-%m-%d"),
                'updated_at': datetime.now().strftime("%Y-%m-%d"),
                'start_date': None,
                'activity_log': [],
                'tasks': [],
                'budget': {
                    'total': 0.0,
                    'currency': 'EUR',
                    'expenses': []
                },
                'team': [],
                'risks': [],
                'swot': {
                    'strengths': [],
                    'weaknesses': [],
                    'opportunities': [],
                    'threats': []
                },
                'decisions': [],
                'bugs': [],
                'stakeholders': [],
                'meetings': [],
                'secrets': [],
                'okrs': [],
                'retros': [],
                'wiki_pages': [],
                'backlog': [],
                'test_cases': [],
                'test_runs': [],
                'automations': [],
                'milestones': [],
                'time_logs': [],
                'documents': []
            }

            self.projects.append(new_project)
            self.save()

            audit_logger.log_project_change(
                username='system',
                project_id=project_id,
                action='project_created',
                details={'title': title, 'category': category}
            )

            logger.info(f"Created new project: {title} ({project_id})")

            return project_id

        except Exception as e:
            error_handler.handle_exception(e, context="add_project")
            return None

    def update_project(self, project_id: str, update_data: Dict) -> bool:
        """Update project with validation"""
        try:
            project = self.get_project(project_id)

            if not project:
                logger.warning(f"Project not found: {project_id}")
                return False

            # Validate specific fields if being updated
            if 'title' in update_data:
                is_valid, error = ProjectValidator.validate_title(update_data['title'])
                if not is_valid:
                    logger.warning(f"Invalid title: {error}")
                    return False
                update_data['title'] = InputValidator.sanitize_string(update_data['title'], 200)

            if 'progress' in update_data:
                is_valid, error = ProjectValidator.validate_progress(update_data['progress'])
                if not is_valid:
                    logger.warning(f"Invalid progress: {error}")
                    return False

            # Update timestamp
            update_data['updated_at'] = datetime.now().strftime("%Y-%m-%d")

            # Apply updates
            project.update(update_data)
            self.save()

            audit_logger.log_project_change(
                username='system',
                project_id=project_id,
                action='project_updated',
                details=update_data
            )

            logger.info(f"Updated project: {project_id}")

            return True

        except Exception as e:
            error_handler.handle_exception(e, context="update_project")
            return False

    def delete_project(self, project_id: str, permanent: bool = False) -> bool:
        """Delete project (soft or permanent)"""
        try:
            if permanent:
                self.projects = [p for p in self.projects if p['id'] != project_id]
                action = 'project_deleted_permanently'
            else:
                project = self.get_project(project_id)
                if project:
                    project['is_deleted'] = True
                    action = 'project_soft_deleted'
                else:
                    return False

            self.save()

            audit_logger.log_project_change(
                username='system',
                project_id=project_id,
                action=action
            )

            logger.info(f"Deleted project: {project_id} (permanent={permanent})")

            return True

        except Exception as e:
            error_handler.handle_exception(e, context="delete_project")
            return False

    def restore_project(self, project_id: str) -> bool:
        """Restore soft-deleted project"""
        return self.update_project(project_id, {'is_deleted': False})

    def duplicate_project(self, template_id: str, new_title: str) -> Optional[str]:
        """Duplicate a project from template"""
        try:
            template = self.get_project(template_id)

            if not template:
                logger.warning(f"Template not found: {template_id}")
                return None

            # Create new project based on template
            new_id = self.add_project(
                title=new_title,
                description=template['description'],
                category=template['category'],
                priority=template['priority'],
                tags=template['tags'].copy()
            )

            if new_id:
                logger.info(f"Duplicated project from template: {template_id} -> {new_id}")

            return new_id

        except Exception as e:
            error_handler.handle_exception(e, context="duplicate_project")
            return None

    # Task Management
    def add_task(
        self,
        project_id: str,
        text: str,
        blocked_by: Optional[str] = None,
        assignee: Optional[str] = None
    ) -> Optional[str]:
        """Add task to project with validation"""
        try:
            # Validate
            is_valid, error = TaskValidator.validate_task_text(text)
            if not is_valid:
                logger.warning(f"Invalid task text: {error}")
                return None

            project = self.get_project(project_id)

            if not project:
                return None

            text = InputValidator.sanitize_string(text, 500)

            task_id = str(uuid.uuid4())

            task = {
                'id': task_id,
                'text': text,
                'status': 'To Do',
                'assignee': assignee,
                'blocked_by': blocked_by,
                'comments': [],
                'created_at': datetime.now().strftime("%Y-%m-%d")
            }

            project['tasks'].append(task)
            self.save()

            logger.info(f"Added task to project {project_id}: {text}")

            return task_id

        except Exception as e:
            error_handler.handle_exception(e, context="add_task")
            return None

    def update_task_status(self, project_id: str, task_id: str, status: str) -> bool:
        """Update task status"""
        try:
            is_valid, error = TaskValidator.validate_task_status(status)
            if not is_valid:
                logger.warning(f"Invalid task status: {error}")
                return False

            project = self.get_project(project_id)

            if not project:
                return False

            for task in project['tasks']:
                if task['id'] == task_id:
                    task['status'] = status

                    if status == 'Done':
                        task['completed_at'] = datetime.now().strftime("%Y-%m-%d")

                    self.save()
                    logger.info(f"Updated task {task_id} status to {status}")
                    return True

            return False

        except Exception as e:
            error_handler.handle_exception(e, context="update_task_status")
            return False

    def delete_task(self, project_id: str, task_id: str) -> bool:
        """Delete task from project"""
        try:
            project = self.get_project(project_id)

            if not project:
                return False

            original_count = len(project['tasks'])
            project['tasks'] = [t for t in project['tasks'] if t['id'] != task_id]

            if len(project['tasks']) < original_count:
                self.save()
                logger.info(f"Deleted task {task_id} from project {project_id}")
                return True

            return False

        except Exception as e:
            error_handler.handle_exception(e, context="delete_task")
            return False

    def add_task_comment(self, project_id: str, task_id: str, comment: str) -> bool:
        """Add comment to task"""
        try:
            project = self.get_project(project_id)

            if not project:
                return False

            comment = InputValidator.sanitize_string(comment, 1000)

            for task in project['tasks']:
                if task['id'] == task_id:
                    task['comments'].append({
                        'text': comment,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
                    })

                    self.save()
                    logger.info(f"Added comment to task {task_id}")
                    return True

            return False

        except Exception as e:
            error_handler.handle_exception(e, context="add_task_comment")
            return False

    def calculate_health(self, project_id: str) -> tuple:
        """Calculate project health status"""
        try:
            project = self.get_project(project_id)

            if not project:
                return "Unknown", "grey"

            # Simple health calculation based on multiple factors
            score = 0

            # Progress factor
            progress = project.get('progress', 0)
            if progress >= 75:
                score += 3
            elif progress >= 50:
                score += 2
            elif progress >= 25:
                score += 1

            # Budget factor
            budget = project.get('budget', {})
            total = budget.get('total', 0)
            spent = sum(e['amount'] for e in budget.get('expenses', []))

            if total > 0:
                budget_ratio = spent / total
                if budget_ratio < 0.8:
                    score += 2
                elif budget_ratio < 1.0:
                    score += 1

            # Task completion factor
            tasks = project.get('tasks', [])
            if tasks:
                done_tasks = len([t for t in tasks if t['status'] == 'Done'])
                task_ratio = done_tasks / len(tasks)

                if task_ratio >= 0.75:
                    score += 2
                elif task_ratio >= 0.5:
                    score += 1

            # Risk factor
            high_risks = len([r for r in project.get('risks', []) if r['prob'] * r['impact'] >= 50])
            if high_risks == 0:
                score += 2
            elif high_risks <= 2:
                score += 1

            # Determine health
            if score >= 7:
                return "Gesund", "green"
            elif score >= 4:
                return "Gefährdet", "orange"
            else:
                return "Kritisch", "red"

        except Exception as e:
            error_handler.handle_exception(e, context="calculate_health")
            return "Unbekannt", "grey"

    def log_activity(self, project_id: str, action: str, user: str = "System"):
        """Log activity to project"""
        try:
            project = self.get_project(project_id)

            if not project:
                return

            project['activity_log'].insert(0, {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'action': action,
                'user': user,
                'project_title': project['title']
            })

            # Keep only last 100 entries
            project['activity_log'] = project['activity_log'][:100]

            self.save()

        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")

    # Budget Management
    def set_budget_total(self, project_id: str, total: float) -> bool:
        """Set project budget total"""
        try:
            is_valid, error = BudgetValidator.validate_expense("Budget", total, "Budget")
            if not is_valid:
                return False

            project = self.get_project(project_id)

            if not project:
                return False

            project['budget']['total'] = float(total)
            self.save()

            self.log_activity(project_id, f"Budget set to {total} EUR")

            return True

        except Exception as e:
            error_handler.handle_exception(e, context="set_budget_total")
            return False

    def add_expense(self, project_id: str, title: str, amount: float, category: str) -> bool:
        """Add expense to project"""
        try:
            is_valid, error = BudgetValidator.validate_expense(title, amount, category)
            if not is_valid:
                logger.warning(f"Invalid expense: {error}")
                return False

            project = self.get_project(project_id)

            if not project:
                return False

            title = InputValidator.sanitize_string(title, 200)

            expense = {
                'title': title,
                'amount': float(amount),
                'category': category,
                'date': datetime.now().strftime("%Y-%m-%d")
            }

            project['budget']['expenses'].append(expense)
            self.save()

            self.log_activity(project_id, f"Added expense: {title} ({amount} EUR)")

            return True

        except Exception as e:
            error_handler.handle_exception(e, context="add_expense")
            return False

    # ... Additional methods for risks, team, milestones, etc. follow the same pattern ...
    # (Implementation continues but truncated for brevity)

    # --- ADDITIONAL PROJECT METHODS ---

    def log_activity(self, project_id: str, action: str, user: str = "System"):
        """Log activity to project"""
        try:
            project = self.get_project(project_id)
            if project:
                if 'activity_log' not in project:
                    project['activity_log'] = []

                project['activity_log'].append({
                    "action": action,
                    "user": user,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                self.save()
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")

    def calculate_health(self, project_id: str) -> Tuple[str, int]:
        """Calculate project health"""
        try:
            project = self.get_project(project_id)
            if not project:
                return ("Unknown", 0)

            score = 100

            # Deadline check
            if project.get('deadline'):
                try:
                    deadline = datetime.strptime(project['deadline'], "%Y-%m-%d")
                    days_left = (deadline - datetime.now()).days
                    if days_left < 0:
                        score -= 30
                    elif days_left < 7:
                        score -= 20
                except:
                    pass

            # Budget check
            budget = project.get('budget', {})
            total = budget.get('total', 0)
            spent = sum(e.get('amount', 0) for e in budget.get('expenses', []))
            if total > 0 and spent > total:
                score -= 20

            # Task completion
            tasks = project.get('tasks', [])
            if tasks:
                completed = len([t for t in tasks if t.get('status') == 'Done'])
                completion_rate = (completed / len(tasks)) * 100
                if completion_rate < 30:
                    score -= 20

            # Health status
            if score >= 80:
                return ("Gesund", score)
            elif score >= 50:
                return ("Moderat", score)
            else:
                return ("Kritisch", score)

        except Exception as e:
            logger.error(f"Error calculating health: {str(e)}")
            return ("Unknown", 0)

    def soft_delete_project(self, project_id: str):
        """Soft delete project"""
        self.update_project(project_id, {"is_deleted": True})
        logger.info(f"Project soft deleted: {project_id}")

    def restore_project(self, project_id: str):
        """Restore soft-deleted project"""
        self.update_project(project_id, {"is_deleted": False})
        logger.info(f"Project restored: {project_id}")

    def delete_project_permanent(self, project_id: str):
        """Permanently delete project"""
        self.projects = [p for p in self.projects if p['id'] != project_id]
        self.save()
        logger.info(f"Project permanently deleted: {project_id}")

    def duplicate_project(self, template_id: str, new_title: str) -> Optional[str]:
        """Duplicate project"""
        try:
            template = self.get_project(template_id)
            if not template:
                return None

            new_project = template.copy()
            new_project['id'] = str(uuid.uuid4())
            new_project['title'] = new_title
            new_project['created_at'] = datetime.now().strftime("%Y-%m-%d")
            new_project['is_template'] = False
            new_project['progress'] = 0
            new_project['status'] = 'Idee'

            self.projects.append(new_project)
            self.save()

            logger.info(f"Project duplicated: {new_title}")
            return new_project['id']

        except Exception as e:
            logger.error(f"Error duplicating project: {str(e)}")
            return None

    # --- TASK MANAGEMENT ---

    def add_task(self, project_id: str, text: str, blocked_by: str = None, assignee: str = None):
        """Add task to project"""
        try:
            project = self.get_project(project_id)
            if project:
                task = {
                    "id": str(uuid.uuid4()),
                    "text": text,
                    "status": "To Do",
                    "assignee": assignee,
                    "comments": []
                }
                project['tasks'].append(task)
                self.save()
                self.log_activity(project_id, f"Task added: {text}")
        except Exception as e:
            logger.error(f"Error adding task: {str(e)}")

    def update_task_status(self, project_id: str, task_id: str, status: str):
        """Update task status"""
        try:
            project = self.get_project(project_id)
            if project:
                for task in project['tasks']:
                    if task['id'] == task_id:
                        task['status'] = status
                        self.save()
                        self.log_activity(project_id, f"Task status updated: {task['text']} -> {status}")
                        break
        except Exception as e:
            logger.error(f"Error updating task status: {str(e)}")

    def delete_task_by_id(self, project_id: str, task_id: str):
        """Delete task by ID"""
        try:
            project = self.get_project(project_id)
            if project:
                project['tasks'] = [t for t in project['tasks'] if t['id'] != task_id]
                self.save()
                self.log_activity(project_id, f"Task deleted")
        except Exception as e:
            logger.error(f"Error deleting task: {str(e)}")

    def add_task_comment(self, project_id: str, task_id: str, comment: str):
        """Add comment to task"""
        try:
            project = self.get_project(project_id)
            if project:
                for task in project['tasks']:
                    if task['id'] == task_id:
                        if 'comments' not in task:
                            task['comments'] = []
                        task['comments'].append({
                            "text": comment,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        self.save()
                        break
        except Exception as e:
            logger.error(f"Error adding task comment: {str(e)}")

    # --- IMAGE MANAGEMENT ---

    def add_image(self, project_id: str, path: str):
        """Add image to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['images'].append(path)
                self.save()
                self.log_activity(project_id, "Image added")
        except Exception as e:
            logger.error(f"Error adding image: {str(e)}")

    def delete_image(self, project_id: str, index: int):
        """Delete image from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['images']):
                del project['images'][index]
                self.save()
                self.log_activity(project_id, "Image deleted")
        except Exception as e:
            logger.error(f"Error deleting image: {str(e)}")

    def delete_all_images(self, project_id: str):
        """Delete all images from project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['images'] = []
                self.save()
                self.log_activity(project_id, "All images deleted")
        except Exception as e:
            logger.error(f"Error deleting all images: {str(e)}")

    # --- DOCUMENT MANAGEMENT ---

    def add_document(self, project_id: str, name: str, path: str):
        """Add document to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['documents'].append({"name": name, "path": path})
                self.save()
                self.log_activity(project_id, f"Document added: {name}")
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")

    def delete_document(self, project_id: str, index: int):
        """Delete document from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['documents']):
                del project['documents'][index]
                self.save()
                self.log_activity(project_id, "Document deleted")
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")

    # --- BUDGET MANAGEMENT ---

    def set_budget_total(self, project_id: str, value: float):
        """Set total budget"""
        try:
            project = self.get_project(project_id)
            if project:
                project['budget']['total'] = value
                self.save()
                self.log_activity(project_id, f"Budget set: {value}")
        except Exception as e:
            logger.error(f"Error setting budget: {str(e)}")

    # --- RISK MANAGEMENT ---

    def add_risk(self, project_id: str, desc: str, prob: int, impact: int):
        """Add risk to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['risks'].append({"desc": desc, "prob": prob, "impact": impact})
                self.save()
                self.log_activity(project_id, f"Risk added: {desc}")
        except Exception as e:
            logger.error(f"Error adding risk: {str(e)}")

    def delete_risk(self, project_id: str, index: int):
        """Delete risk from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['risks']):
                del project['risks'][index]
                self.save()
                self.log_activity(project_id, "Risk deleted")
        except Exception as e:
            logger.error(f"Error deleting risk: {str(e)}")

    # --- TEAM MANAGEMENT ---

    def add_team_member(self, project_id: str, name: str, role: str):
        """Add team member to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['team'].append({"name": name, "role": role})
                self.save()
                self.log_activity(project_id, f"Team member added: {name}")
        except Exception as e:
            logger.error(f"Error adding team member: {str(e)}")

    def delete_team_member(self, project_id: str, index: int):
        """Delete team member from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['team']):
                del project['team'][index]
                self.save()
                self.log_activity(project_id, "Team member deleted")
        except Exception as e:
            logger.error(f"Error deleting team member: {str(e)}")

    # --- MILESTONE MANAGEMENT ---

    def add_milestone(self, project_id: str, title: str, date: str):
        """Add milestone to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['milestones'].append({"title": title, "date": date, "done": False})
                self.save()
                self.log_activity(project_id, f"Milestone added: {title}")
        except Exception as e:
            logger.error(f"Error adding milestone: {str(e)}")

    def toggle_milestone(self, project_id: str, index: int):
        """Toggle milestone done status"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['milestones']):
                project['milestones'][index]['done'] = not project['milestones'][index]['done']
                self.save()
                self.log_activity(project_id, "Milestone toggled")
        except Exception as e:
            logger.error(f"Error toggling milestone: {str(e)}")

    def delete_milestone(self, project_id: str, index: int):
        """Delete milestone from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['milestones']):
                del project['milestones'][index]
                self.save()
                self.log_activity(project_id, "Milestone deleted")
        except Exception as e:
            logger.error(f"Error deleting milestone: {str(e)}")

    # --- TIME LOG MANAGEMENT ---

    def add_time_log(self, project_id: str, date: str, category: str, hours: float, desc: str):
        """Add time log to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['time_logs'].append({
                    "date": date,
                    "category": category,
                    "hours": hours,
                    "desc": desc
                })
                self.save()
                self.log_activity(project_id, f"Time logged: {hours}h")
        except Exception as e:
            logger.error(f"Error adding time log: {str(e)}")

    # --- REMAINING METHODS (SWOT, OKR, Wiki, etc.) ---

    def add_decision(self, project_id: str, title: str, status: str, rationale: str):
        """Add decision to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['decisions'].append({"title": title, "status": status, "rationale": rationale})
                self.save()
        except Exception as e:
            logger.error(f"Error adding decision: {str(e)}")

    def delete_decision(self, project_id: str, index: int):
        """Delete decision from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['decisions']):
                del project['decisions'][index]
                self.save()
        except Exception as e:
            logger.error(f"Error deleting decision: {str(e)}")

    def add_bug(self, project_id: str, title: str, severity: str):
        """Add bug to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['bugs'].append({"title": title, "severity": severity, "status": "Open"})
                self.save()
        except Exception as e:
            logger.error(f"Error adding bug: {str(e)}")

    def toggle_bug(self, project_id: str, index: int):
        """Toggle bug status"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['bugs']):
                bug = project['bugs'][index]
                bug['status'] = "Fixed" if bug['status'] == "Open" else "Open"
                self.save()
        except Exception as e:
            logger.error(f"Error toggling bug: {str(e)}")

    def delete_bug(self, project_id: str, index: int):
        """Delete bug from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['bugs']):
                del project['bugs'][index]
                self.save()
        except Exception as e:
            logger.error(f"Error deleting bug: {str(e)}")

    def add_stakeholder(self, project_id: str, name: str, org: str, influence: str):
        """Add stakeholder to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['stakeholders'].append({"name": name, "org": org, "influence": influence})
                self.save()
        except Exception as e:
            logger.error(f"Error adding stakeholder: {str(e)}")

    def delete_stakeholder(self, project_id: str, index: int):
        """Delete stakeholder from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['stakeholders']):
                del project['stakeholders'][index]
                self.save()
        except Exception as e:
            logger.error(f"Error deleting stakeholder: {str(e)}")

    def add_meeting(self, project_id: str, date: str, title: str, summary: str):
        """Add meeting to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['meetings'].append({"date": date, "title": title, "summary": summary})
                self.save()
        except Exception as e:
            logger.error(f"Error adding meeting: {str(e)}")

    def delete_meeting(self, project_id: str, index: int):
        """Delete meeting from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['meetings']):
                del project['meetings'][index]
                self.save()
        except Exception as e:
            logger.error(f"Error deleting meeting: {str(e)}")

    def add_secret(self, project_id: str, key: str, value: str):
        """Add secret to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['secrets'].append({"key": key, "value": value})
                self.save()
        except Exception as e:
            logger.error(f"Error adding secret: {str(e)}")

    def delete_secret(self, project_id: str, index: int):
        """Delete secret from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['secrets']):
                del project['secrets'][index]
                self.save()
        except Exception as e:
            logger.error(f"Error deleting secret: {str(e)}")

    def add_swot(self, project_id: str, category: str, text: str):
        """Add SWOT item to project"""
        try:
            project = self.get_project(project_id)
            if project and 'swot' in project:
                if category in project['swot']:
                    project['swot'][category].append(text)
                    self.save()
        except Exception as e:
            logger.error(f"Error adding SWOT: {str(e)}")

    def delete_swot(self, project_id: str, category: str, index: int):
        """Delete SWOT item from project"""
        try:
            project = self.get_project(project_id)
            if project and 'swot' in project:
                if category in project['swot'] and index < len(project['swot'][category]):
                    del project['swot'][category][index]
                    self.save()
        except Exception as e:
            logger.error(f"Error deleting SWOT: {str(e)}")

    def add_okr(self, project_id: str, objective: str):
        """Add OKR to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['okrs'].append({"id": str(uuid.uuid4()), "objective": objective, "key_results": []})
                self.save()
        except Exception as e:
            logger.error(f"Error adding OKR: {str(e)}")

    def delete_okr(self, project_id: str, index: int):
        """Delete OKR from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['okrs']):
                del project['okrs'][index]
                self.save()
        except Exception as e:
            logger.error(f"Error deleting OKR: {str(e)}")

    def add_key_result(self, project_id: str, okr_id: str, title: str, progress: int):
        """Add key result to OKR"""
        try:
            project = self.get_project(project_id)
            if project:
                for okr in project['okrs']:
                    if okr['id'] == okr_id:
                        okr['key_results'].append({"title": title, "progress": progress})
                        self.save()
                        break
        except Exception as e:
            logger.error(f"Error adding key result: {str(e)}")

    def add_retro(self, project_id: str, category: str, text: str):
        """Add retro item to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['retros'].append({"category": category, "text": text})
                self.save()
        except Exception as e:
            logger.error(f"Error adding retro: {str(e)}")

    def delete_retro(self, project_id: str, index: int):
        """Delete retro from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['retros']):
                del project['retros'][index]
                self.save()
        except Exception as e:
            logger.error(f"Error deleting retro: {str(e)}")

    def add_wiki_page(self, project_id: str, title: str, content: str):
        """Add wiki page to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['wiki_pages'].append({"title": title, "content": content})
                self.save()
        except Exception as e:
            logger.error(f"Error adding wiki page: {str(e)}")

    def update_wiki_page(self, project_id: str, index: int, title: str, content: str):
        """Update wiki page"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['wiki_pages']):
                project['wiki_pages'][index] = {"title": title, "content": content}
                self.save()
        except Exception as e:
            logger.error(f"Error updating wiki page: {str(e)}")

    def delete_wiki_page(self, project_id: str, index: int):
        """Delete wiki page from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['wiki_pages']):
                del project['wiki_pages'][index]
                self.save()
        except Exception as e:
            logger.error(f"Error deleting wiki page: {str(e)}")

    def add_backlog_item(self, project_id: str, title: str, priority: str):
        """Add backlog item to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['backlog'].append({"title": title, "priority": priority})
                self.save()
        except Exception as e:
            logger.error(f"Error adding backlog item: {str(e)}")

    def delete_backlog_item(self, project_id: str, index: int):
        """Delete backlog item from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['backlog']):
                del project['backlog'][index]
                self.save()
        except Exception as e:
            logger.error(f"Error deleting backlog item: {str(e)}")

    def add_test_case(self, project_id: str, title: str, steps: str, expected: str):
        """Add test case to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['test_cases'].append({
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "steps": steps,
                    "expected": expected,
                    "status": "Untested"
                })
                self.save()
        except Exception as e:
            logger.error(f"Error adding test case: {str(e)}")

    def update_test_status(self, project_id: str, test_id: str, status: str):
        """Update test case status"""
        try:
            project = self.get_project(project_id)
            if project:
                for test in project['test_cases']:
                    if test['id'] == test_id:
                        test['status'] = status
                        self.save()
                        break
        except Exception as e:
            logger.error(f"Error updating test status: {str(e)}")

    def delete_test_case(self, project_id: str, index: int):
        """Delete test case from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['test_cases']):
                del project['test_cases'][index]
                self.save()
        except Exception as e:
            logger.error(f"Error deleting test case: {str(e)}")

    def add_automation(self, project_id: str, trigger: str, action: str):
        """Add automation to project"""
        try:
            project = self.get_project(project_id)
            if project:
                project['automations'].append({"trigger": trigger, "action": action})
                self.save()
        except Exception as e:
            logger.error(f"Error adding automation: {str(e)}")

    def delete_automation(self, project_id: str, index: int):
        """Delete automation from project"""
        try:
            project = self.get_project(project_id)
            if project and index < len(project['automations']):
                del project['automations'][index]
                self.save()
        except Exception as e:
            logger.error(f"Error deleting automation: {str(e)}")

    # --- EXPERIMENT MANAGEMENT ---

    def add_experiment(self, name: str, description: str, category: str,
                      tester: str, project_id: Optional[str] = None) -> str:
        """Add new experiment"""
        try:
            experiment = {
                "id": str(uuid.uuid4()),
                "name": name,
                "description": description,
                "category": category,
                "tester": tester,
                "project_id": project_id,
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "status": "Geplant",
                "samples": [],
                "matrix_columns": ["Ergebnis"],
                "matrix_data": [],
                "images": [],
                "result_summary": "",
                "conclusion": "Offen"
            }

            self.experiments.append(experiment)
            self.save_experiments()
            logger.info(f"Experiment created: {name}")
            return experiment["id"]

        except Exception as e:
            logger.error(f"Error creating experiment: {str(e)}")
            return None

    def get_experiment(self, exp_id: str) -> Optional[Dict]:
        """Get experiment by ID"""
        return next((e for e in self.experiments if e["id"] == exp_id), None)

    def update_experiment_matrix(self, exp_id: str, samples: List[Dict],
                                columns: List[str], data: List[Dict]):
        """Update experiment matrix structure and data"""
        try:
            for exp in self.experiments:
                if exp["id"] == exp_id:
                    exp["samples"] = samples
                    exp["matrix_columns"] = columns
                    exp["matrix_data"] = data
                    exp["status"] = "Laufend"
                    self.save_experiments()
                    logger.info(f"Experiment matrix updated: {exp_id}")
                    return

        except Exception as e:
            logger.error(f"Error updating experiment matrix: {str(e)}")

    def update_experiment_meta(self, exp_id: str, summary: str,
                              conclusion: str, status: str):
        """Update experiment metadata"""
        try:
            for exp in self.experiments:
                if exp["id"] == exp_id:
                    exp["result_summary"] = summary
                    exp["conclusion"] = conclusion
                    exp["status"] = status
                    self.save_experiments()
                    logger.info(f"Experiment meta updated: {exp_id}")
                    return

        except Exception as e:
            logger.error(f"Error updating experiment meta: {str(e)}")

    def add_experiment_image(self, exp_id: str, path: str, caption: str = ""):
        """Add image to experiment"""
        try:
            for exp in self.experiments:
                if exp["id"] == exp_id:
                    exp["images"].append({"path": path, "caption": caption})
                    self.save_experiments()
                    logger.info(f"Image added to experiment: {exp_id}")
                    return

        except Exception as e:
            logger.error(f"Error adding experiment image: {str(e)}")

    def delete_experiment_image(self, exp_id: str, idx: int):
        """Delete experiment image"""
        try:
            for exp in self.experiments:
                if exp["id"] == exp_id:
                    del exp["images"][idx]
                    self.save_experiments()
                    logger.info(f"Image deleted from experiment: {exp_id}")
                    return

        except Exception as e:
            logger.error(f"Error deleting experiment image: {str(e)}")

    def delete_experiment(self, exp_id: str):
        """Delete experiment"""
        try:
            self.experiments = [e for e in self.experiments if e["id"] != exp_id]
            self.save_experiments()
            logger.info(f"Experiment deleted: {exp_id}")

        except Exception as e:
            logger.error(f"Error deleting experiment: {str(e)}")


# Singleton instance
_project_manager = None


def get_project_manager() -> ProjectManager:
    """Get singleton ProjectManager instance"""
    global _project_manager

    if _project_manager is None:
        _project_manager = ProjectManager()

    return _project_manager
