# Django Roles AJAX - Data Science Club Management System

A Django web application for managing Data Science Club projects and courses with role-based access control.

## Features

- **User Authentication**: Login, logout, registration, password reset
- **Three Role System**:
  - Normal Users: can view and apply to projects, browse courses
  - Staff/Mentors: are managing courses, can accept/reject applications from users to projects, are mentoring projects
  - Admins: Full system access including user management
- **Projects Management**: Browse, filter (by categories), and apply to projects
- **Courses System**: Browse and filter courses by programming languages and difficulty levels
- **AJAX Technology**: Dynamic filtering and updates without page reload
- **Responsive Design**: Bootstrap 5 with mobile-friendly interface
- **Profile Management**: Users can change their password, email, and username

## Technology Stack

- Python 3.13
- Django 5.2
- Bootstrap 5.3.0
- Bootstrap Icons
- SQLite Database
- Docker & Docker Compose

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually comes with Docker Desktop)
- Python (tested version 3.13.0)
- Django (tested version 5.2)

## Quick Start with Docker

### Step 1: Start the application

```bash
# Build and start containers
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d --build
```

The application will be available at http://localhost:8000 (but database is empty, you can still register users though)

### Step 2: Initialize database (in another terminal: in case of no '-d' option)

```bash
# Works on Windows, Linux, and macOS
python init_db.py
```

This will automatically:
- Run migrations
- Create categories
- Create courses and programming languages
- Generate test users and projects
- User credentials will be saved in test_users_credentials.txt

## Default Test Accounts

After running `python init_db.py`, use these credentials:

- **Admin**: username: `admin`, password: `admin123`
- **Mentors**: `mentor1-mentor3`, passwords: `mentorpass1-mentorpass3`
- **Users**: `user1-user10`, passwords: `testpass1-testpass10`

All credentials are saved in `test_users_credentials.txt`

## Project Structure

```
.
├── core/               # Main application
│   ├── management/     # Custom management commands
│   ├── migrations/     # Database migrations
│   ├── templates/      # HTML templates
│   ├── forms.py        # Form definitions
│   ├── models.py       # Database models
│   ├── urls.py         # URL routing
│   └── views.py        # View functions
├── project/            # Django project settings
│   └── settings.py     # Configuration
├── static/             # Static files (CSS, JS)
├── manage.py           # Django management script
├── Dockerfile          # Docker configuration
└── docker-compose.yml  # Docker Compose
```

## Endpoints

- `/` - Home/Dashboard
- `/login/` - User login
- `/register/` - User registration
- `/projects/` - Browse projects
- `/courses/` - Browse courses
- `/profile/edit/` - Edit user profile
- `/admin/` - Django admin panel (admin only)

## Testing

This project includes comprehensive unit and integration tests with 70%+ code coverage.

### Run Tests

```bash
# Make sure Docker containers are running
docker-compose up -d

# Run tests with coverage
python run_tests.py
```

After running the script information will show in terminal and also detailed report will available in `htmlcov/index.html`.

## License

MIT License - Educational project for Web Application Programming course.
