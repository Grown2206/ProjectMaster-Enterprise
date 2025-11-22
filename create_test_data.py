"""
Test Data Generator for ProjectMaster Enterprise
Creates 2-3 sample projects and experiments with comprehensive data
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_manager_v2 import get_project_manager
from config import Config

def create_test_projects():
    """Create 2-3 comprehensive test projects"""

    manager = get_project_manager()
    print("🚀 Creating test projects...\n")

    # Project 1: AI-Powered Customer Service Platform
    print("📁 Creating Project 1: AI Customer Service Platform...")

    project1_id = manager.add_project(
        title="AI-Powered Customer Service Platform",
        description="Entwicklung einer KI-gestützten Kundenservice-Plattform mit Natural Language Processing und automatisierten Antworten.",
        category="IT",
        priority="High",
        deadline=(datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
        tags=["AI", "NLP", "Machine Learning"]
    )

    if project1_id:
        # Update status and progress
        project1 = manager.get_project(project1_id)
        project1['status'] = 'In Arbeit'
        project1['progress'] = 35
        project1['budget']['total'] = 150000.0

        # Add tasks
        manager.add_task(project1_id, "NLP Model Training", "High")
        manager.update_task_status(project1_id, 0, "Done")
        manager.add_task(project1_id, "API Integration", "High")
        manager.update_task_status(project1_id, 1, "In Progress")
        manager.add_task(project1_id, "Frontend Dashboard", "Med")
        manager.add_task(project1_id, "Unit Tests", "Med")

        # Add team
        manager.add_team_member(project1_id, "Dr. Sarah Chen", "AI Lead")
        manager.add_team_member(project1_id, "Marcus Weber", "Backend Dev")

        # Add milestones
        manager.add_milestone(project1_id, "Beta Launch", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
        manager.add_milestone(project1_id, "Production Release", (datetime.now() + timedelta(days=75)).strftime("%Y-%m-%d"))

        # Add risks
        manager.add_risk(project1_id, "NLP Accuracy unter 85%", 50, 80)

        manager.save()
        print(f"  ✅ Created with tasks, team, milestones\n")

    # Project 2: E-Commerce Mobile App
    print("📁 Creating Project 2: E-Commerce Mobile App...")

    project2_id = manager.add_project(
        title="ShopEasy Mobile App Relaunch 2.0",
        description="Komplette Überarbeitung unserer E-Commerce App mit modernem Design und AR Features.",
        category="IT",
        priority="Critical",
        deadline=(datetime.now() + timedelta(days=120)).strftime("%Y-%m-%d"),
        tags=["Mobile", "E-Commerce", "React Native", "AR"]
    )

    if project2_id:
        project2 = manager.get_project(project2_id)
        project2['status'] = 'Planung'
        project2['progress'] = 15
        project2['budget']['total'] = 200000.0

        # Add tasks
        manager.add_task(project2_id, "User Research & Interviews", "High")
        manager.update_task_status(project2_id, 0, "Done")
        manager.add_task(project2_id, "UI/UX Design Mockups", "High")
        manager.update_task_status(project2_id, 1, "In Progress")
        manager.add_task(project2_id, "AR Framework Integration", "Med")
        manager.add_task(project2_id, "Payment Gateway Migration", "High")

        # Add team
        manager.add_team_member(project2_id, "Lisa Müller", "Product Manager")
        manager.add_team_member(project2_id, "Kevin Park", "Mobile Lead")
        manager.add_team_member(project2_id, "Anna Kowalski", "UX Designer")

        # Add milestones
        manager.add_milestone(project2_id, "Design Phase Complete", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
        manager.add_milestone(project2_id, "App Store Launch", (datetime.now() + timedelta(days=120)).strftime("%Y-%m-%d"))

        # Add stakeholders
        manager.add_stakeholder(project2_id, "Michael Schmidt", "Management", "High")

        # Add bug
        manager.add_bug(project2_id, "Checkout crashes on iOS 14", "High")

        manager.save()
        print(f"  ✅ Created with tasks, team, stakeholders\n")

    # Project 3: Cloud Migration
    print("📁 Creating Project 3: Cloud Infrastructure Migration...")

    project3_id = manager.add_project(
        title="AWS Cloud Infrastructure Migration",
        description="Migration aller On-Premise Services zu AWS Cloud mit Kubernetes.",
        category="IT",
        priority="High",
        deadline=(datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
        tags=["Cloud", "AWS", "Kubernetes", "DevOps"]
    )

    if project3_id:
        project3 = manager.get_project(project3_id)
        project3['status'] = 'Review'
        project3['progress'] = 65
        project3['budget']['total'] = 180000.0

        # Add tasks
        manager.add_task(project3_id, "AWS Account Setup", "Critical")
        manager.update_task_status(project3_id, 0, "Done")
        manager.add_task(project3_id, "EKS Cluster Deployment", "High")
        manager.update_task_status(project3_id, 1, "Done")
        manager.add_task(project3_id, "Database Migration", "Critical")
        manager.update_task_status(project3_id, 2, "In Progress")
        manager.add_task(project3_id, "CI/CD Pipeline", "High")
        manager.add_task(project3_id, "Security Audit", "High")

        # Add team
        manager.add_team_member(project3_id, "Robert Johnson", "Cloud Architect")
        manager.add_team_member(project3_id, "Yuki Tanaka", "DevOps Engineer")

        # Add milestones
        manager.add_milestone(project3_id, "Production Migration", (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"))
        manager.toggle_milestone(project3_id, 0)  # Mark as done

        # Add risks
        manager.add_risk(project3_id, "Data Loss bei Migration", 20, 100)
        manager.add_risk(project3_id, "AWS Kosten höher als geplant", 70, 50)

        # Add automations
        manager.add_automation(project3_id, "Daily at 2AM", "Backup Database")

        manager.save()
        print(f"  ✅ Created with tasks, team, automations\n")

    print(f"✅ Successfully created 3 test projects!\n")
    return [project1_id, project2_id, project3_id]


def create_test_experiments():
    """Create 2-3 test experiments"""

    manager = get_project_manager()
    print("🧪 Creating test experiments...\n")

    # Experiment 1: A/B Test - Button Color
    print("🧬 Creating Experiment 1: Button Color A/B Test...")

    exp1_id = manager.add_experiment(
        name="CTA Button Color Optimization",
        description="A/B Test zur Optimierung der Conversion Rate durch verschiedene Button-Farben. Hypothese: Ein grüner CTA Button erhöht die Conversion Rate um 15%.",
        category="Marketing",
        tester="Lisa Müller"
    )

    print(f"  ✅ Created: CTA Button Color Optimization\n")

    # Experiment 2: Feature Flag - Dark Mode
    print("🧬 Creating Experiment 2: Dark Mode Feature Flag...")

    exp2_id = manager.add_experiment(
        name="Dark Mode Feature Rollout",
        description="Schrittweise Einführung des Dark Mode Features. Hypothese: Dark Mode erhöht Session Duration um 20%.",
        category="IT",
        tester="Kevin Park"
    )

    print(f"  ✅ Created: Dark Mode Feature Rollout\n")

    # Experiment 3: Multivariate Test
    print("🧬 Creating Experiment 3: Product Page Layout Test...")

    exp3_id = manager.add_experiment(
        name="Product Page Layout Optimization",
        description="Multivariate Test mit verschiedenen Layout-Kombinationen. Hypothese: Große Hero Images erhöhen Add-to-Cart Rate um 25%.",
        category="Marketing",
        tester="Anna Kowalski"
    )

    print(f"  ✅ Created: Product Page Layout Optimization\n")

    print(f"✅ Successfully created 3 test experiments!\n")
    return [exp1_id, exp2_id, exp3_id]


def create_test_users():
    """Create test users"""

    manager = get_project_manager()
    print("👥 Creating test users...\n")

    users = [
        {"username": "admin", "password": "admin123", "role": "Admin", "name": "Administrator"},
        {"username": "sarah.chen", "password": "password123", "role": "Project Manager", "name": "Dr. Sarah Chen"},
        {"username": "lisa.mueller", "password": "password123", "role": "Product Manager", "name": "Lisa Müller"}
    ]

    for user in users:
        if manager.add_user(**user):
            print(f"  ✅ Created user: {user['username']} ({user['role']})")

    print()


def main():
    """Main function to create all test data"""

    print("=" * 60)
    print("🎯 ProjectMaster Enterprise - Test Data Generator")
    print("=" * 60)
    print()

    # Ensure data directory exists
    Config.ensure_directories()

    try:
        # Create test users
        create_test_users()

        # Create test projects
        project_ids = create_test_projects()

        # Create test experiments
        experiment_ids = create_test_experiments()

        print("=" * 60)
        print("🎉 TEST DATA CREATION COMPLETE!")
        print("=" * 60)
        print()
        print(f"📊 Summary:")
        print(f"  • {len(project_ids)} Projects created")
        print(f"  • {len(experiment_ids)} Experiments created")
        print(f"  • 3 Users created")
        print()
        print("🚀 You can now start the application with:")
        print("   streamlit run main.py")
        print()

    except Exception as e:
        print(f"\n❌ Error creating test data: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
