# Django Roles AJAX - Data Science Club Management System

A Django web application for managing Data Science Club projects and courses with role-based access control. Normal users are Data Science Club participants who can browse courses to learn new things. They can also browse DS Club projects and apply to participate in them. Mentors are experienced DS Club participants who can create, edit, and delete courses, become mentors of projects, and accept or deny user applications to projects. Finally, admins have full control over the app. They can do everything previous users can do, plus create, edit, delete projects and manage users.

## Features

- **User Authentication**: Login, logout, registration, login/email/password reset
- **Three Role System**:
  - Normal Users: can view and apply to projects, browse courses
  - Staff/Mentors: are managing courses, can accept/reject applications from users to projects, are mentoring projects
  - Admins: Full system access including user management
- **Projects Management**: Browse, filter (by categories), and apply to projects
- **Courses System**: Browse and filter courses by programming languages and difficulty levels
- **AJAX Technology**: Dynamic filtering and updates without page reload
- **Responsive Design**: Bootstrap 5 with mobile-friendly interface
- **Profile Management**: Users can change their password, email, and username

## Main App's views 

The navigation bar at the top is always visible. After logging in, users can see their username and logout button on the right. The DataScienceClub button redirects to a page about the DS Club. The Home button always redirects to the Dashboard page after logging in.



### Login Page

On the login page, users can register a new account and view the DSClub page.

![Login Page](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/01_login_page.png)

![Register Page](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/02_register.png)


### Normal users view

#### Dashboard
The first page that every user sees is the Dashboard, which displays their username, email, role, and quick statistics. After logging in, users can also see a sidebar on the left. Depending on the role, the higher it is, the more content is visible.

![Dashboard](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/03_dashboard.png)

Normal users can see a list of projects where they can apply to participate. They can also filter projects.

![Projects list](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/04_projects.png)

They can also see a similar list of courses on another page.

![Courses list](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/05_courses.png)

They can also change their personal information on the last page from the sidebar.

![Edit profile page](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/06_edit_info.png)




### Staff / Mentors view
The Dashboard looks pretty much the same, but on the projects or courses page we can see additional permissions in play.

On the projects list page, they can confirm or deny user applications, remove current users from a project, and become mentors for projects.

![Projects list for Mentors](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/07_mentor_projects.png)

On the courses list page, they can now edit or delete a course. On the sidebar, Mentors also have the option to add new courses.

![Courses page for Mentors](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/08_mentor_courses.png)

![Adding new course](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/09_mentor_newcourse.png)

### Admin view
Admins are users with the highest role. On the projects page, they have the option to edit or delete projects, as well as all Mentor options.

![Projects list for Admins](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/10_admin_projects.png)

The courses view for Admins is no different than the one for Mentors.

On the sidebar, they can see new content available only to Admins. They can add new projects and manage users.

![Adding new project](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/11_admin_newproject.png)

On the manage users page, they can completely delete any user account, including Mentors. Admins can change the role of any user to any new role. Admins can also assign users to projects. Admins cannot delete their own account.

![Managing Users](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/12_admin_manageusers.png)


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

![Test score](https://raw.githubusercontent.com/Pablo1337PL/Web-App-in-Django/main/main_views/tests.png)

### Run Tests

```bash
# Make sure Docker containers are running
docker-compose up -d

# Run tests with coverage
python run_tests.py
```

After running the script, information will be displayed in the terminal and a detailed report will be available in `htmlcov/index.html`.

## License

MIT License - Educational project for Web Application Programming course.
