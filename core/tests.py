from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import (
    Project, Category, Assignment, Application, UserProfile,
    Course, ProgrammingLanguage
)
from core.forms import (
    UserRegisterForm, ProjectForm, CourseForm,
    ChangePasswordForm, ChangeEmailForm, ChangeUsernameForm
)
import json


# ========================
# MODEL TESTS
# ========================

class CategoryModelTest(TestCase):
    def test_category_creation(self):
        """Test creating a category"""
        category = Category.objects.create(name="Machine Learning")
        self.assertEqual(str(category), "Machine Learning")
        self.assertEqual(category.name, "Machine Learning")

    def test_category_unique_name(self):
        """Test that category names must be unique"""
        Category.objects.create(name="AI")
        with self.assertRaises(Exception):
            Category.objects.create(name="AI")


class ProjectModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Data Science")
        self.mentor = User.objects.create_user(
            username="mentor1",
            password="test123",
            is_staff=True
        )

    def test_project_creation(self):
        """Test creating a project"""
        project = Project.objects.create(
            name="Test Project",
            description="Test description"
        )
        self.assertEqual(str(project), "Test Project")
        self.assertEqual(project.name, "Test Project")

    def test_project_without_name(self):
        """Test project without name returns 'Unnamed Project'"""
        project = Project.objects.create(description="No name project")
        self.assertEqual(str(project), "Unnamed Project")

    def test_project_categories(self):
        """Test many-to-many relationship with categories"""
        project = Project.objects.create(name="ML Project", description="Test")
        project.categories.add(self.category)
        self.assertEqual(project.categories.count(), 1)
        self.assertIn(self.category, project.categories.all())

    def test_project_mentors(self):
        """Test many-to-many relationship with mentors"""
        project = Project.objects.create(name="Mentor Project", description="Test")
        project.mentors.add(self.mentor)
        self.assertEqual(project.mentors.count(), 1)
        self.assertIn(self.mentor, project.mentors.all())


class AssignmentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="test123")
        self.project = Project.objects.create(name="Project 1", description="Test")

    def test_assignment_creation(self):
        """Test creating an assignment"""
        assignment = Assignment.objects.create(
            user=self.user,
            project=self.project
        )
        self.assertEqual(str(assignment), "user1 → Project 1")

    def test_assignment_unique_together(self):
        """Test that user-project combination is unique"""
        Assignment.objects.create(user=self.user, project=self.project)
        with self.assertRaises(Exception):
            Assignment.objects.create(user=self.user, project=self.project)


class ApplicationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="applicant", password="test123")
        self.project = Project.objects.create(name="Project A", description="Test")

    def test_application_creation(self):
        """Test creating an application"""
        app = Application.objects.create(
            user=self.user,
            project=self.project,
            status='pending'
        )
        self.assertEqual(str(app), "applicant → Project A (pending)")
        self.assertEqual(app.status, 'pending')

    def test_application_status_choices(self):
        """Test application status changes"""
        app = Application.objects.create(user=self.user, project=self.project)
        self.assertEqual(app.status, 'pending')

        app.status = 'accepted'
        app.save()
        self.assertEqual(app.status, 'accepted')

    def test_application_unique_together(self):
        """Test that user-project combination is unique"""
        Application.objects.create(user=self.user, project=self.project)
        with self.assertRaises(Exception):
            Application.objects.create(user=self.user, project=self.project)


class ProgrammingLanguageModelTest(TestCase):
    def test_programming_language_creation(self):
        """Test creating a programming language"""
        lang = ProgrammingLanguage.objects.create(name="Python")
        self.assertEqual(str(lang), "Python")

    def test_programming_language_unique(self):
        """Test that language names must be unique"""
        ProgrammingLanguage.objects.create(name="JavaScript")
        with self.assertRaises(Exception):
            ProgrammingLanguage.objects.create(name="JavaScript")


class CourseModelTest(TestCase):
    def setUp(self):
        self.lang = ProgrammingLanguage.objects.create(name="Python")

    def test_course_creation(self):
        """Test creating a course"""
        course = Course.objects.create(
            name="Python Basics",
            description="Learn Python",
            level=1
        )
        self.assertEqual(str(course), "Python Basics (Level 1)")
        self.assertEqual(course.level, 1)
        self.assertEqual(course.get_level_display(), 'Beginner')

    def test_course_programming_languages(self):
        """Test many-to-many relationship with programming languages"""
        course = Course.objects.create(
            name="Advanced Programming",
            description="Test",
            level=4
        )
        course.programming_languages.add(self.lang)
        self.assertEqual(course.programming_languages.count(), 1)
        self.assertIn(self.lang, course.programming_languages.all())


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")

    def test_user_profile_creation(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), "testuser")
        self.assertEqual(profile.user, self.user)


# ========================
# FORM TESTS
# ========================

class UserRegisterFormTest(TestCase):
    def test_valid_registration_form(self):
        """Test valid user registration form"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_registration_form_passwords_dont_match(self):
        """Test invalid form when passwords don't match"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_registration_form_missing_email(self):
        """Test form is invalid without email"""
        form_data = {
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())


class ProjectFormTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Web Development")

    def test_valid_project_form(self):
        """Test valid project form"""
        form_data = {
            'name': 'New Project',
            'description': 'Project description',
            'categories': [self.category.id]
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_project_form_without_name(self):
        """Test project form without name"""
        form_data = {
            'description': 'Description only'
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())  # Name is nullable


class CourseFormTest(TestCase):
    def setUp(self):
        self.lang = ProgrammingLanguage.objects.create(name="Java")

    def test_valid_course_form(self):
        """Test valid course form"""
        form_data = {
            'name': 'Java Programming',
            'description': 'Learn Java',
            'level': 2,
            'programming_languages': [self.lang.id]
        }
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_course_form_invalid_level(self):
        """Test course form with invalid level"""
        form_data = {
            'name': 'Invalid Course',
            'description': 'Test',
            'level': 10  # Invalid level
        }
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())


class ChangePasswordFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="oldpass123")

    def test_valid_password_change(self):
        """Test valid password change form"""
        form_data = {
            'old_password': 'oldpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_old_password(self):
        """Test form is invalid with wrong old password"""
        form_data = {
            'old_password': 'wrongpass',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())

    def test_passwords_dont_match(self):
        """Test form is invalid when new passwords don't match"""
        form_data = {
            'old_password': 'oldpass123',
            'new_password1': 'newpass123',
            'new_password2': 'different123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())

    def test_password_too_short(self):
        """Test form is invalid when password is too short"""
        form_data = {
            'old_password': 'oldpass123',
            'new_password1': 'short',
            'new_password2': 'short'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())


class ChangeEmailFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", email="user1@test.com", password="test123")
        self.user2 = User.objects.create_user(username="user2", email="user2@test.com", password="test123")

    def test_valid_email_change(self):
        """Test valid email change"""
        form_data = {'email': 'newemail@test.com'}
        form = ChangeEmailForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_duplicate_email(self):
        """Test form is invalid when email is already in use"""
        form_data = {'email': 'user2@test.com'}
        form = ChangeEmailForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())


class ChangeUsernameFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="test123")
        self.user2 = User.objects.create_user(username="user2", password="test123")

    def test_valid_username_change(self):
        """Test valid username change"""
        form_data = {'username': 'newusername'}
        form = ChangeUsernameForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_duplicate_username(self):
        """Test form is invalid when username is already taken"""
        form_data = {'username': 'user2'}
        form = ChangeUsernameForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())

    def test_username_too_short(self):
        """Test form is invalid when username is too short"""
        form_data = {'username': 'ab'}
        form = ChangeUsernameForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())


# ========================
# VIEW TESTS
# ========================

class AuthenticationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="test123")
        UserProfile.objects.create(user=self.user)

    def test_register_view_get(self):
        """Test GET request to register view"""
        response = self.client.get(reverse('core:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'username')

    def test_register_view_post_valid(self):
        """Test POST request to register with valid data"""
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        response = self.client.post(reverse('core:register'), data)
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)
        self.assertEqual(UserProfile.objects.filter(user__username='newuser').count(), 1)

    def test_login_required_for_home(self):
        """Test that home page requires login"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_home_view_authenticated(self):
        """Test home view for authenticated user"""
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """Test logout functionality"""
        self.client.login(username='testuser', password='test123')
        response = self.client.post(reverse('core:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout


class ProjectViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="test123")
        self.staff = User.objects.create_user(username="staff1", password="test123", is_staff=True)
        self.category = Category.objects.create(name="AI")
        self.project = Project.objects.create(name="AI Project", description="Test AI")
        self.project.categories.add(self.category)

    def test_project_list_requires_login(self):
        """Test that project list requires login"""
        response = self.client.get(reverse('core:project_list'))
        self.assertEqual(response.status_code, 302)

    def test_project_list_authenticated(self):
        """Test project list for authenticated user"""
        self.client.login(username='user1', password='test123')
        response = self.client.get(reverse('core:project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Projects')  # Page loads with title

    def test_project_list_with_search(self):
        """Test project list with search query"""
        self.client.login(username='user1', password='test123')
        response = self.client.get(reverse('core:project_list') + '?q=AI')
        self.assertEqual(response.status_code, 200)

    def test_project_list_ajax(self):
        """Test AJAX request to project list"""
        self.client.login(username='user1', password='test123')
        response = self.client.get(
            reverse('core:project_list'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('projects', data)

    def test_add_project_requires_staff(self):
        """Test that adding project requires staff permission"""
        self.client.login(username='user1', password='test123')
        response = self.client.get(reverse('core:add_project'))
        self.assertEqual(response.status_code, 302)  # Redirect (permission denied)

    def test_add_project_staff(self):
        """Test staff can access add project page"""
        self.client.login(username='staff1', password='test123')
        response = self.client.get(reverse('core:add_project'))
        self.assertEqual(response.status_code, 200)

    def test_edit_project_staff(self):
        """Test staff can edit project"""
        self.client.login(username='staff1', password='test123')
        response = self.client.get(reverse('core:edit_project', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_project_staff(self):
        """Test staff can delete project"""
        self.client.login(username='staff1', password='test123')
        response = self.client.post(reverse('core:delete_project', args=[self.project.id]))
        self.assertEqual(Project.objects.filter(id=self.project.id).count(), 0)


class ApplicationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="test123")
        self.staff = User.objects.create_user(username="staff1", password="test123", is_staff=True)
        self.project = Project.objects.create(name="Project 1", description="Test")

    def test_apply_to_project(self):
        """Test user can apply to project"""
        self.client.login(username='user1', password='test123')
        response = self.client.post(reverse('core:apply_to_project', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Application.objects.filter(user=self.user, project=self.project).count(), 1)

    def test_staff_cannot_apply(self):
        """Test staff cannot apply to projects"""
        self.client.login(username='staff1', password='test123')
        response = self.client.post(reverse('core:apply_to_project', args=[self.project.id]))
        self.assertEqual(response.status_code, 403)

    def test_accept_application(self):
        """Test staff can accept application"""
        app = Application.objects.create(user=self.user, project=self.project, status='pending')
        self.client.login(username='staff1', password='test123')
        response = self.client.get(reverse('core:accept_application', args=[app.id]))
        app.refresh_from_db()
        self.assertEqual(app.status, 'accepted')
        self.assertEqual(Assignment.objects.filter(user=self.user, project=self.project).count(), 1)

    def test_reject_application(self):
        """Test staff can reject application"""
        app = Application.objects.create(user=self.user, project=self.project, status='pending')
        self.client.login(username='staff1', password='test123')
        response = self.client.get(reverse('core:reject_application', args=[app.id]))
        app.refresh_from_db()
        self.assertEqual(app.status, 'rejected')


class CourseViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="test123")
        self.staff = User.objects.create_user(username="staff1", password="test123", is_staff=True)
        self.lang = ProgrammingLanguage.objects.create(name="Python")
        self.course = Course.objects.create(
            name="Python Basics",
            description="Learn Python",
            level=1
        )
        self.course.programming_languages.add(self.lang)

    def test_courses_list_requires_login(self):
        """Test courses list requires login"""
        response = self.client.get(reverse('core:courses_list'))
        self.assertEqual(response.status_code, 302)

    def test_courses_list_authenticated(self):
        """Test courses list for authenticated user"""
        self.client.login(username='user1', password='test123')
        response = self.client.get(reverse('core:courses_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Courses')  # Page loads with title

    def test_courses_list_ajax(self):
        """Test AJAX request to courses list"""
        self.client.login(username='user1', password='test123')
        response = self.client.get(
            reverse('core:courses_list'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('courses', data)

    def test_add_course_requires_staff(self):
        """Test that adding course requires staff permission"""
        self.client.login(username='user1', password='test123')
        response = self.client.get(reverse('core:add_course'))
        self.assertEqual(response.status_code, 302)

    def test_add_course_staff(self):
        """Test staff can add course"""
        self.client.login(username='staff1', password='test123')
        response = self.client.get(reverse('core:add_course'))
        self.assertEqual(response.status_code, 200)

    def test_edit_course_staff(self):
        """Test staff can edit course"""
        self.client.login(username='staff1', password='test123')
        response = self.client.get(reverse('core:edit_course', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_course_staff(self):
        """Test staff can delete course"""
        self.client.login(username='staff1', password='test123')
        response = self.client.post(reverse('core:delete_course', args=[self.course.id]))
        self.assertEqual(Course.objects.filter(id=self.course.id).count(), 0)


class ProfileEditViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="oldpass123"
        )

    def test_profile_edit_requires_login(self):
        """Test profile edit requires login"""
        response = self.client.get(reverse('core:profile_edit'))
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_get(self):
        """Test GET request to profile edit"""
        self.client.login(username='testuser', password='oldpass123')
        response = self.client.get(reverse('core:profile_edit'))
        self.assertEqual(response.status_code, 200)

    def test_change_password(self):
        """Test changing password"""
        self.client.login(username='testuser', password='oldpass123')
        data = {
            'change_password': True,
            'old_password': 'oldpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        response = self.client.post(reverse('core:profile_edit'), data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    def test_change_email(self):
        """Test changing email"""
        self.client.login(username='testuser', password='oldpass123')
        data = {
            'change_email': True,
            'email': 'newemail@test.com'
        }
        response = self.client.post(reverse('core:profile_edit'), data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@test.com')

    def test_change_username(self):
        """Test changing username"""
        self.client.login(username='testuser', password='oldpass123')
        data = {
            'change_username': True,
            'username': 'newusername'
        }
        response = self.client.post(reverse('core:profile_edit'), data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newusername')


class MentorViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(username="staff1", password="test123", is_staff=True)
        self.project = Project.objects.create(name="Project 1", description="Test")

    def test_mentor_project(self):
        """Test staff can become mentor"""
        self.client.login(username='staff1', password='test123')
        response = self.client.post(reverse('core:mentor_project', args=[self.project.id]))
        self.project.refresh_from_db()
        self.assertIn(self.staff, self.project.mentors.all())

    def test_unmentor_project(self):
        """Test staff can stop mentoring"""
        self.project.mentors.add(self.staff)
        self.client.login(username='staff1', password='test123')
        response = self.client.post(reverse('core:unmentor_project', args=[self.project.id]))
        self.project.refresh_from_db()
        self.assertNotIn(self.staff, self.project.mentors.all())


class AdminViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin",
            password="test123",
            is_staff=True,
            is_superuser=True
        )
        self.user = User.objects.create_user(username="user1", password="test123")

    def test_admin_manage_users(self):
        """Test admin can access user management"""
        self.client.login(username='admin', password='test123')
        response = self.client.get(reverse('core:admin_manage_users'))
        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        """Test admin can delete user"""
        self.client.login(username='admin', password='test123')
        response = self.client.post(reverse('core:delete_user', args=[self.user.id]))
        self.assertEqual(User.objects.filter(id=self.user.id).count(), 0)

    def test_change_user_role(self):
        """Test admin can change user role"""
        self.client.login(username='admin', password='test123')
        data = {'role': 'staff'}
        response = self.client.post(reverse('core:change_user_role', args=[self.user.id]), data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)


# ========================
# URL TESTS
# ========================

class URLTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123", is_staff=True)
        self.project = Project.objects.create(name="Test", description="Test")
        self.course = Course.objects.create(name="Test Course", description="Test", level=1)
        self.app = Application.objects.create(user=self.user, project=self.project)
        self.assignment = Assignment.objects.create(user=self.user, project=self.project)

    def test_url_home(self):
        """Test home URL resolves correctly"""
        url = reverse('core:home')
        self.assertEqual(url, '/')

    def test_url_register(self):
        """Test register URL resolves correctly"""
        url = reverse('core:register')
        self.assertEqual(url, '/register/')

    def test_url_projects(self):
        """Test projects URL resolves correctly"""
        url = reverse('core:project_list')
        self.assertEqual(url, '/projects/')

    def test_url_courses(self):
        """Test courses URL resolves correctly"""
        url = reverse('core:courses_list')
        self.assertEqual(url, '/courses/')

    def test_url_add_project(self):
        """Test add project URL resolves correctly"""
        url = reverse('core:add_project')
        self.assertEqual(url, '/staff/projects/add/')

    def test_url_edit_project(self):
        """Test edit project URL resolves correctly"""
        url = reverse('core:edit_project', args=[self.project.id])
        self.assertEqual(url, f'/staff/projects/edit/{self.project.id}/')

    def test_url_add_course(self):
        """Test add course URL resolves correctly"""
        url = reverse('core:add_course')
        self.assertEqual(url, '/staff/courses/add/')

    def test_url_profile_edit(self):
        """Test profile edit URL resolves correctly"""
        url = reverse('core:profile_edit')
        self.assertEqual(url, '/profile/edit/')
