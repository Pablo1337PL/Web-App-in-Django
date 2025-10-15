#!/usr/bin/env python3
"""
Reset migrations script - Consolidates all migrations into one clean file.
Works on Windows, Linux, and macOS.
"""

import subprocess
import sys
import platform
import os

def run_command(command, description):
    """Run a command"""
    print(f"\n{description}...")
    print(f"Command: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("Django Roles AJAX - Reset Migrations")
    print("=" * 60)
    print(f"Platform: {platform.system()}")
    print()
    print("WARNING: This will:")
    print("  - Delete the database (db.sqlite3)")
    print("  - Delete all migration files")
    print("  - Create one fresh migration file")
    print("  - Reinitialize all data")
    print()

    response = input("Do you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        sys.exit(0)

    # Check if docker-compose is available
    try:
        subprocess.run(["docker-compose", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Docker Compose is not installed or not in PATH")
        print("Please install Docker and Docker Compose first")
        sys.exit(1)

    print("\nStarting migration reset...\n")

    # Step 1: Stop containers
    print("Stopping Docker containers...")
    run_command("docker-compose down", "Stopping containers")

    # Step 2: Delete database
    print("\nDeleting database...")
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
        print("  Deleted: db.sqlite3")
    else:
        print("  Database file not found (already deleted)")

    # Step 3: Delete migration files (keep __init__.py)
    print("\nDeleting migration files...")
    migrations_dir = "core/migrations"
    if os.path.exists(migrations_dir):
        for filename in os.listdir(migrations_dir):
            if filename.startswith("0") and filename.endswith(".py"):
                filepath = os.path.join(migrations_dir, filename)
                os.remove(filepath)
                print(f"  Deleted: {filepath}")

    # Step 4: Start containers
    print("\nStarting Docker containers...")
    if not run_command("docker-compose up -d", "Starting containers"):
        sys.exit(1)

    # Wait a moment for containers to be ready
    print("\nWaiting for containers to be ready...")
    import time
    time.sleep(3)

    # Step 5: Create fresh migrations
    print("\nCreating fresh migrations...")
    if not run_command("docker-compose exec web python manage.py makemigrations", "Creating migrations"):
        sys.exit(1)

    # Step 6: Apply migrations
    print("\nApplying migrations...")
    if not run_command("docker-compose exec web python manage.py migrate", "Applying migrations"):
        sys.exit(1)

    # Step 7: Initialize data
    print("\n" + "=" * 60)
    print("Migrations reset complete!")
    print("=" * 60)
    print()
    print("Now run the initialization script to create data:")
    print("  python init_db.py")
    print()

if __name__ == "__main__":
    main()
