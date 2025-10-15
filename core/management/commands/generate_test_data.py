import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from core.models import Project, Category, Assignment, Application, UserProfile


class Command(BaseCommand):
    help = 'Generate test data: 20 projects, 10 users, 3 mentors'

    def handle(self, *args, **kwargs):
        # Clear existing data (optional - comment out if you want to keep existing data)
        self.stdout.write("Clearing existing test data...")
        User.objects.filter(is_superuser=False).delete()
        Project.objects.all().delete()

        credentials = []

        # Project names and descriptions
        project_names = [
            "Customer Churn Prediction",
            "Sales Forecasting Model",
            "Image Classification System",
            "Sentiment Analysis Tool",
            "Recommendation Engine",
            "Fraud Detection System",
            "Time Series Analysis",
            "Natural Language Processing Bot",
            "Computer Vision Application",
            "Big Data Pipeline",
            "Market Basket Analysis",
            "Neural Network Research",
            "Deep Learning Framework",
            "Data Visualization Dashboard",
            "Predictive Maintenance System",
            "Speech Recognition Model",
            "Text Generation AI",
            "Anomaly Detection Tool",
            "Clustering Analysis Project",
            "Reinforcement Learning Game"
        ]

        descriptions = [
            "Analyzing customer behavior patterns to predict churn rates using machine learning algorithms.",
            "Building predictive models to forecast sales trends based on historical data.",
            "Developing a deep learning model for multi-class image classification tasks.",
            "Creating sentiment analysis tools for social media monitoring and brand reputation.",
            "Implementing collaborative filtering and content-based recommendation systems.",
            "Detecting fraudulent transactions using ensemble learning techniques.",
            "Analyzing temporal patterns and forecasting future trends in time series data.",
            "Building conversational AI systems using natural language understanding.",
            "Applying computer vision techniques for object detection and recognition.",
            "Creating scalable data processing pipelines for large-scale datasets.",
            "Discovering purchasing patterns and associations in retail transaction data.",
            "Researching novel neural network architectures for improved performance.",
            "Developing frameworks for training and deploying deep learning models.",
            "Creating interactive dashboards for data exploration and insights.",
            "Predicting equipment failures before they occur using sensor data.",
            "Building models for converting speech to text with high accuracy.",
            "Generating human-like text using transformer-based language models.",
            "Identifying unusual patterns and outliers in complex datasets.",
            "Grouping similar data points using unsupervised learning algorithms.",
            "Training intelligent agents using reinforcement learning techniques."
        ]

        # Create 10 normal users
        self.stdout.write("Creating 10 normal users...")
        for i in range(1, 11):
            username = f"user{i}"
            password = f"testpass{i}"
            email = f"user{i}@example.com"

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=False,
                is_superuser=False
            )
            UserProfile.objects.get_or_create(user=user)
            credentials.append(f"Username: {username}, Password: {password}, Email: {email}, Role: User")
            self.stdout.write(f"  Created user: {username}")

        # Create 3 mentors (staff users)
        self.stdout.write("Creating 3 mentors...")
        for i in range(1, 4):
            username = f"mentor{i}"
            password = f"mentorpass{i}"
            email = f"mentor{i}@example.com"

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=False
            )
            UserProfile.objects.get_or_create(user=user)
            credentials.append(f"Username: {username}, Password: {password}, Email: {email}, Role: Mentor (Staff)")
            self.stdout.write(f"  Created mentor: {username}")

        # Create 1 admin user
        self.stdout.write("Creating admin user...")
        admin_username = "admin"
        admin_password = "admin123"
        admin_email = "admin@example.com"

        # Delete existing admin user if it exists
        User.objects.filter(username=admin_username).delete()

        admin_user = User.objects.create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            is_staff=True,
            is_superuser=True
        )
        UserProfile.objects.get_or_create(user=admin_user)
        credentials.append(f"Username: {admin_username}, Password: {admin_password}, Email: {admin_email}, Role: Admin (Superuser)")
        self.stdout.write(f"  Created admin: {admin_username}")

        # Get all categories
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(self.style.WARNING("No categories found. Run 'python manage.py create_categories' first."))
            return

        # Create 20 projects
        self.stdout.write("Creating 20 projects...")
        projects = []
        for i in range(20):
            project = Project.objects.create(
                name=project_names[i],
                description=descriptions[i]
            )

            # Assign 1-3 random categories to each project
            num_categories = random.randint(1, 3)
            selected_categories = random.sample(categories, num_categories)
            project.categories.set(selected_categories)

            projects.append(project)
            self.stdout.write(f"  Created project: {project.name}")

        # Get all users and mentors
        normal_users = list(User.objects.filter(is_staff=False, is_superuser=False))
        mentors = list(User.objects.filter(is_staff=True, is_superuser=False))

        # Assign mentors to projects (each project gets 0-2 mentors)
        self.stdout.write("Assigning mentors to projects...")
        for project in projects:
            num_mentors = random.randint(0, 2)
            if num_mentors > 0:
                selected_mentors = random.sample(mentors, min(num_mentors, len(mentors)))
                project.mentors.set(selected_mentors)
                mentor_names = ", ".join([m.username for m in selected_mentors])
                self.stdout.write(f"  {project.name}: {mentor_names}")

        # Assign users to projects (each project gets 1-4 users)
        self.stdout.write("Assigning users to projects...")
        for project in projects:
            num_users = random.randint(1, 4)
            selected_users = random.sample(normal_users, min(num_users, len(normal_users)))

            for user in selected_users:
                # Create accepted application and assignment
                Application.objects.create(
                    user=user,
                    project=project,
                    status='accepted'
                )
                Assignment.objects.create(
                    user=user,
                    project=project
                )

            user_names = ", ".join([u.username for u in selected_users])
            self.stdout.write(f"  {project.name}: {user_names}")

        # Create some pending applications (2-3 random applications)
        self.stdout.write("Creating some pending applications...")
        for _ in range(3):
            user = random.choice(normal_users)
            project = random.choice(projects)

            # Check if user already has application/assignment for this project
            if not Application.objects.filter(user=user, project=project).exists():
                Application.objects.create(
                    user=user,
                    project=project,
                    status='pending'
                )
                self.stdout.write(f"  {user.username} applied to {project.name}")

        # Write credentials to file
        output_file = settings.BASE_DIR / 'test_users_credentials.txt'
        with open(output_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("TEST USER CREDENTIALS\n")
            f.write("=" * 60 + "\n\n")

            f.write("NORMAL USERS (10):\n")
            f.write("-" * 60 + "\n")
            for cred in credentials[:10]:
                f.write(cred + "\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("MENTORS / STAFF (3):\n")
            f.write("-" * 60 + "\n")
            for cred in credentials[10:13]:
                f.write(cred + "\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("ADMIN (1):\n")
            f.write("-" * 60 + "\n")
            f.write(credentials[13] + "\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("SUMMARY:\n")
            f.write("-" * 60 + "\n")
            f.write(f"Total Projects: {len(projects)}\n")
            f.write(f"Total Normal Users: {len(normal_users)}\n")
            f.write(f"Total Mentors: {len(mentors)}\n")
            f.write(f"Total Admins: 1\n")
            f.write(f"Total Assignments: {Assignment.objects.count()}\n")
            f.write(f"Pending Applications: {Application.objects.filter(status='pending').count()}\n")
            f.write("=" * 60 + "\n")

        self.stdout.write(self.style.SUCCESS(f"\nTest data generated successfully!"))
        self.stdout.write(self.style.SUCCESS(f"Credentials saved to: {output_file}"))
