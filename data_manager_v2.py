"""
Data Manager Module v2.0
Enhanced project management with proper error handling, validation, and logging
"""

import json
import os
import uuid
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Any
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
        self.users_file = DataPaths.DATA_DIR / "users_data.json"
        self.users = self._load_users()

        # Experiments management
        self.experiments_file = DataPaths.DATA_DIR / "experiments_data.json"
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
        audit_logger.info(f"User created: {username} (role: {role})")
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
