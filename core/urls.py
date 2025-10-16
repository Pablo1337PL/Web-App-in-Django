from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('datasciencepage/', views.datasciencepage, name='datasciencepage'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Auth routes
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Password reset routes (simplified - doesn't send emails)
    path('password_reset/', views.password_reset_request, name='password_reset'),

    # Project routes
    path("projects/", views.project_list, name="project_list"),
    path("projects/apply/<int:project_id>/", views.apply_to_project, name="apply_to_project"),

    # Course routes
    path("courses/", views.courses_list, name="courses_list"),
    path("staff/courses/add/", views.add_course, name="add_course"),
    path("staff/courses/edit/<int:course_id>/", views.edit_course, name="edit_course"),
    path("staff/courses/delete/<int:course_id>/", views.delete_course, name="delete_course"),

    # Application routes
    path("projects/accept/<int:application_id>/", views.accept_application, name="accept_application"),
    path("projects/reject/<int:application_id>/", views.reject_application, name="reject_application"),
    path("projects/remove/<int:assignment_id>/", views.remove_user_from_project, name="remove_user_from_project"),

    # Staff routes
    path('projects/mentor/<int:project_id>/', views.mentor_project, name='mentor_project'),
    path('projects/unmentor/<int:project_id>/', views.unmentor_project, name='unmentor_project'),

    # Admin routes
    path('admin/projects/add/', views.add_project, name='add_project'),
    path('admin/projects/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('admin/projects/delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('admin/users/', views.admin_manage_users, name='admin_manage_users'),
    path('admin/users/assign/<int:user_id>/', views.assign_user_to_project, name='assign_user_to_project'),
    path('admin/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin/users/change-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
]

