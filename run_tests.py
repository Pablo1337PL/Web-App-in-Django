#!/usr/bin/env python3
"""
Test runner script for Django Roles AJAX project.
Works on Windows, Linux, and macOS.
"""

import subprocess
import sys
import platform

def run_command(command, description):
    """Run a docker-compose command"""
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
    print("Django Roles AJAX - Test Runner")
    print("=" * 60)
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
        ("Installing coverage", "docker-compose exec web pip install coverage==7.6.9"),
        ("Running tests with coverage", "docker-compose exec web coverage run --source='core' --omit='*/migrations/*,*/tests.py' manage.py test core"),
        ("Generating coverage report", "docker-compose exec web coverage report"),
        ("Generating HTML coverage report", "docker-compose exec web coverage html"),
    ]

    print("Starting test execution...\n")

    for description, command in commands:
        if not run_command(command, description):
            print(f"\nFailed at: {description}")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("Tests completed successfully!")
    print("=" * 60)
    print()
    print("To view detailed HTML coverage report:")
    print("  Open: htmlcov/index.html in your browser")
    print()
    print("Coverage files generated:")
    print("  - .coverage (raw coverage data)")
    print("  - htmlcov/ (HTML report directory)")
    print()

if __name__ == "__main__":
    main()
