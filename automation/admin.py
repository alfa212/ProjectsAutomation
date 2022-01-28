from django.contrib import admin
from django.urls import re_path
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect

from .models import Student, Manager, Group, Project
from .forms import StudentImportForm


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    change_list_template = "admin/model_change_list.html"
    list_display = ('tg_username', 'name', 'level')
    list_filter = ['level']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path('^import/$', self.admin_site.admin_view(self.import_students), name='import-students'),
        ]

        return custom_urls + urls

    def import_students(self, request):
        if request.method != 'POST':
            form = StudentImportForm()
        else:
            form = StudentImportForm(request.POST, request.FILES)

            if form.is_valid():
                students = form.save()

                for student in students:
                    Student.objects.update_or_create(
                        tg_username=student['tg_username'],
                        name=student['name'],
                        level=student['level'],
                        discord_username=student['discord_username'],
                        is_far_east=student['is_far_east'],
                        time=student['time_from']
                    )

                return HttpResponseRedirect('../')

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['title'] = "Импорт студентов"
        


        return TemplateResponse(
            request,
            'admin/students/students_import.html',
            context,
        )

admin.site.register(Manager)
admin.site.register(Group)
admin.site.register(Project)