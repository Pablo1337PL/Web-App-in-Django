from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from core.models import Project, Assignment, UserProfile, Application, Category, Course, ProgrammingLanguage
from django.contrib.admin.views.decorators import staff_member_required, user_passes_test
from .forms import AssignUserForm, UserRegisterForm, ProjectForm, CourseForm, ChangePasswordForm, ChangeEmailForm, ChangeUsernameForm


def password_reset_request(request):
    """Simple password reset that doesn't send emails, just redirects to login"""
    if request.method == 'POST':
        messages.info(request, "Password reset link would be sent to your email. (Feature not configured)")
        return redirect('core:login')
    return render(request, 'registration/password_reset.html')


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, "Konto zostało utworzone! Możesz się zalogować.")
            return redirect('core:login')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})


def datasciencepage(request):
    return render(request, 'core/data_science.html')


@require_POST
def logout_view(request):
    """Custom logout view that clears messages"""
    # Clear all messages before logging out
    storage = get_messages(request)
    for _ in storage:
        pass  # Iterate to clear
    logout(request)
    return redirect('core:login')


@login_required
def home_view(request):
    # Get user statistics
    user_projects_count = Assignment.objects.filter(user=request.user).count()
    pending_applications_count = Application.objects.filter(user=request.user, status='pending').count()

    # Get mentor statistics for staff
    mentor_projects_count = 0
    if request.user.is_staff:
        mentor_projects_count = Project.objects.filter(mentors=request.user).count()

    context = {
        'user_projects_count': user_projects_count,
        'pending_applications_count': pending_applications_count,
        'mentor_projects_count': mentor_projects_count,
    }
    return render(request, 'core/home.html', context)


@login_required
def profile_edit(request):
    password_form = ChangePasswordForm(user=request.user)
    email_form = ChangeEmailForm(user=request.user, initial={'email': request.user.email})
    username_form = ChangeUsernameForm(user=request.user, initial={'username': request.user.username})

    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = ChangePasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                # Re-authenticate the user to update the session
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
                messages.success(request, "Your password has been changed successfully.")
                return redirect('core:profile_edit')

        elif 'change_email' in request.POST:
            email_form = ChangeEmailForm(user=request.user, data=request.POST)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, "Your email has been changed successfully.")
                return redirect('core:profile_edit')

        elif 'change_username' in request.POST:
            username_form = ChangeUsernameForm(user=request.user, data=request.POST)
            if username_form.is_valid():
                username_form.save()
                messages.success(request, "Your username has been changed successfully.")
                return redirect('core:profile_edit')

    context = {
        'password_form': password_form,
        'email_form': email_form,
        'username_form': username_form,
    }
    return render(request, 'core/profile_edit.html', context)


def is_admin(user):
    return user.is_superuser


def is_staff_user(user):
    return user.is_staff or user.is_superuser


def is_admin_user(user):
    return user.is_superuser


@login_required
def project_list(request):
    projects = Project.objects.all().prefetch_related('categories')

    # Get all categories for the filter dropdown
    all_categories = Category.objects.all()

    # Filter by search query
    search_query = request.GET.get('q', '')
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Filter by multiple categories if provided
    category_filters = request.GET.getlist('category')
    if category_filters:
        # Show projects that have at least one of the selected categories
        projects = projects.filter(categories__id__in=category_filters).distinct()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for p in projects:
            # Get accepted users (assignments) with assignment IDs
            accepted_users = []
            for a in p.assignment_set.all():
                accepted_users.append({
                    'username': a.user.username,
                    'assignment_id': a.id
                })

            # Get pending applications with application IDs
            pending_applications = []
            if request.user.is_staff:
                pending_apps = Application.objects.filter(project=p, status='pending')
                for app in pending_apps:
                    pending_applications.append({
                        'username': app.user.username,
                        'application_id': app.id
                    })

            # Check if current user has already applied or is accepted
            user_application = Application.objects.filter(user=request.user, project=p).first()
            user_is_assigned = Assignment.objects.filter(user=request.user, project=p).exists()

            can_apply = not request.user.is_staff and not user_application and not user_is_assigned

            # Get categories for this project
            categories = [{"id": c.id, "name": c.name} for c in p.categories.all()]

            # Get mentors for this project
            mentors = [{"username": m.username, "id": m.id} for m in p.mentors.all()]

            # Check if current user is mentoring this project
            is_mentoring = request.user.is_staff and p.mentors.filter(id=request.user.id).exists()

            data.append({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "categories": categories,
                "participants": accepted_users,
                "mentors": mentors,
                "is_mentoring": is_mentoring,
                "pending_applications": pending_applications,
                "can_apply": can_apply,
                "is_staff": request.user.is_staff,
                "is_admin": request.user.is_superuser,
                "user_status": user_application.status if user_application else None,
            })
        return JsonResponse({"projects": data})

    return render(request, "core/project_list.html", {
        "projects": projects,
        "all_categories": all_categories,
    })


@login_required
def courses_list(request):
    courses = Course.objects.all().prefetch_related('programming_languages')

    # Get all programming languages for the filter
    all_languages = ProgrammingLanguage.objects.all()

    # Filter by search query
    search_query = request.GET.get('q', '')
    if search_query:
        courses = courses.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Filter by multiple programming languages if provided
    language_filters = request.GET.getlist('language')
    if language_filters:
        # Show courses that have at least one of the selected languages
        courses = courses.filter(programming_languages__id__in=language_filters).distinct()

    # Filter by level if provided
    level_filter = request.GET.get('level', '')
    if level_filter:
        courses = courses.filter(level=level_filter)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for c in courses:
            # Get programming languages for this course
            languages = [{"id": lang.id, "name": lang.name} for lang in c.programming_languages.all()]

            data.append({
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "level": c.level,
                "level_display": c.get_level_display(),
                "programming_languages": languages,
                "is_staff": request.user.is_staff,
            })
        return JsonResponse({"courses": data})

    return render(request, "core/courses_list.html", {
        "courses": courses,
        "all_languages": all_languages,
    })


@login_required
@user_passes_test(is_staff_user)
def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Course added successfully.")
            return redirect("core:courses_list")
    else:
        form = CourseForm()
    return render(request, "core/add_course.html", {"form": form})


@login_required
@user_passes_test(is_staff_user)
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully.")
            return redirect("core:courses_list")
    else:
        form = CourseForm(instance=course)
    return render(request, "core/edit_course.html", {"form": form, "course": course})


@login_required
@user_passes_test(is_staff_user)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully.")
        return redirect("core:courses_list")
    return redirect("core:courses_list")


@login_required
@require_POST
def apply_to_project(request, project_id):
    """Regular users apply to projects (creates pending application)"""
    if request.user.is_staff:
        return JsonResponse({"success": False, "message": "Staff cannot apply"}, status=403)

    project = get_object_or_404(Project, id=project_id)

    # Check if already applied or assigned
    if Application.objects.filter(user=request.user, project=project).exists():
        return JsonResponse({"success": False, "message": "Already applied"}, status=400)

    if Assignment.objects.filter(user=request.user, project=project).exists():
        return JsonResponse({"success": False, "message": "Already assigned"}, status=400)

    Application.objects.create(user=request.user, project=project, status='pending')
    return JsonResponse({"success": True, "message": "Application submitted"})


@login_required
@user_passes_test(is_staff_user)
def accept_application(request, application_id):
    """Staff accepts a pending application and creates assignment"""
    application = get_object_or_404(Application, id=application_id)

    if application.status == 'pending':
        application.status = 'accepted'
        application.save()

        # Create assignment
        Assignment.objects.get_or_create(user=application.user, project=application.project)
        messages.success(request, f"{application.user.username} has been accepted to {application.project.name}")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": True, "message": "Application accepted"})
    return redirect('core:project_list')


@login_required
@user_passes_test(is_staff_user)
def reject_application(request, application_id):
    """Staff rejects a pending application"""
    application = get_object_or_404(Application, id=application_id)

    if application.status == 'pending':
        application.status = 'rejected'
        application.save()
        messages.success(request, f"Application from {application.user.username} has been rejected")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": True, "message": "Application rejected"})
    return redirect('core:project_list')


@login_required
@user_passes_test(is_staff_user)
@require_POST
def remove_user_from_project(request, assignment_id):
    """Staff removes an assigned user from project"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    user = assignment.user
    project = assignment.project

    # Delete the assignment
    assignment.delete()

    # Also delete the application so user can apply again
    Application.objects.filter(user=user, project=project).delete()

    # Check for AJAX request (Django converts header names to lowercase with underscores)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        return JsonResponse({"success": True, "message": f"{user.username} removed from {project.name}"})

    messages.success(request, f"{user.username} has been removed from {project.name}")
    return redirect('core:project_list')


@login_required
@user_passes_test(is_staff_user)
def add_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Project added successfully.")
            return redirect("core:project_list")
    else:
        form = ProjectForm()
    return render(request, "core/add_project.html", {"form": form})


@login_required
@user_passes_test(is_staff_user)
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully.")
            return redirect("core:project_list")
    else:
        form = ProjectForm(instance=project)
    return render(request, "core/edit_project.html", {"form": form, "project": project})


@login_required
@user_passes_test(is_staff_user)
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted.")
        return redirect("core:project_list")
    return redirect("core:project_list")


@login_required
@user_passes_test(is_staff_user)
def admin_manage_users(request):
    user_profiles = UserProfile.objects.select_related("user").all()
    return render(request, "core/admin_manage_users.html", {"user_profiles": user_profiles})


@login_required
@user_passes_test(is_staff_user)
def assign_user_to_project(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        project_id = request.POST.get("project_id")
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            Assignment.objects.get_or_create(user=user, project=project)
            messages.success(request, f"{user.username} assigned to {project.name}.")
            return redirect("core:admin_manage_users")

    # Get all projects with search capability
    search_query = request.GET.get('q', '')
    projects = Project.objects.all()

    if search_query:
        projects = projects.filter(name__icontains=search_query)

    # Get projects user is already assigned to
    assigned_project_ids = Assignment.objects.filter(user=user).values_list('project_id', flat=True)

    return render(request, "core/assign_user_to_project.html", {
        "user": user,
        "projects": projects,
        "assigned_project_ids": assigned_project_ids,
        "search_query": search_query,
    })


@login_required
@user_passes_test(is_admin_user)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted successfully.")
    return redirect("core:admin_manage_users")


@login_required
@user_passes_test(is_staff_user)
@require_POST
def mentor_project(request, project_id):
    """Staff can assign themselves as mentor to a project"""
    project = get_object_or_404(Project, id=project_id)

    # Add the current user as a mentor
    project.mentors.add(request.user)
    messages.success(request, f"You are now mentoring {project.name}.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": True, "message": "You are now mentoring this project"})
    return redirect("core:project_list")


@login_required
@user_passes_test(is_staff_user)
@require_POST
def unmentor_project(request, project_id):
    """Staff can remove themselves as mentor from a project"""
    project = get_object_or_404(Project, id=project_id)

    # Remove the current user as a mentor
    project.mentors.remove(request.user)
    messages.success(request, f"You are no longer mentoring {project.name}.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": True, "message": "You are no longer mentoring this project"})
    return redirect("core:project_list")


@login_required
@user_passes_test(is_admin_user)
@require_POST
def change_user_role(request, user_id):
    """Admin can change user role"""
    user = get_object_or_404(User, id=user_id)
    new_role = request.POST.get('role')

    if new_role == 'admin':
        user.is_staff = True
        user.is_superuser = True
    elif new_role == 'staff':
        user.is_staff = True
        user.is_superuser = False
    elif new_role == 'user':
        user.is_staff = False
        user.is_superuser = False
    else:
        messages.error(request, "Invalid role")
        return redirect("core:admin_manage_users")

    user.save()
    messages.success(request, f"Role changed for {user.username} to {new_role}")
    return redirect("core:admin_manage_users")
