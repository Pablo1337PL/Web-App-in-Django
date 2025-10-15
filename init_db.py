#!/usr/bin/env python3
"""
Database initialization script for Django Roles AJAX project.
Works on Windows, Linux, and macOS.
"""

import subprocess
import sys
import platform

def run_command(command):
    """Run a docker-compose command"""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def main():
    print("Initializing database...")
    print(f"Platform: {platform.system()}")
    print()

    # Check if docker-compose is available
    try:
        subprocess.run(["docker-compose", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Docker Compose is not installed or not in PATH")
        print("Please install Docker and Docker Compose first")
        sys.exit(1)

    commands = [
        ("Running migrations", "docker-compose exec web python manage.py migrate"),
        ("Creating categories", "docker-compose exec web python manage.py create_categories"),
        ("Creating courses and programming languages", "docker-compose exec web python manage.py create_courses"),
        ("Generating test data", "docker-compose exec web python manage.py generate_test_data"),
    ]

    print("Starting initialization...\n")

    for description, command in commands:
        print(f"{description}...")
        if not run_command(command):
            print(f"Failed at: {description}")
            sys.exit(1)
        print()

    print("=" * 60)
    print("Database initialized successfully!")
    print("=" * 60)
    print()
    print("Test credentials saved to: test_users_credentials.txt")
    print("Access the application at: http://localhost:8000")
    print()
    print("Test accounts:")
    print("  - Users: user1-user10 (password: testpass1-testpass10)")
    print("  - Mentors: mentor1-mentor3 (password: mentorpass1-mentorpass3)")
    print("  - Admin: admin (password: admin123)")
    print()

if __name__ == "__main__":
    main()
