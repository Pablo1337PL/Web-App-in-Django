from django.contrib import admin
from .models import Project, Assignment, UserProfile, Application, Category

admin.site.register(Project)
admin.site.register(Assignment)
admin.site.register(UserProfile)
admin.site.register(Application)
admin.site.register(Category)
