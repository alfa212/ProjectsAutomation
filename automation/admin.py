from django.contrib import admin

from .models import Student, Manager, Group, Project

admin.site.register(Student)
admin.site.register(Manager)
admin.site.register(Group)
admin.site.register(Project)