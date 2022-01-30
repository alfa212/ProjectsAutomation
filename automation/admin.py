from django.contrib import admin
from django.urls import re_path, reverse
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.utils.html import format_html


from .models import Student, Manager, Group, Project, LonelyStudent
from .forms import StudentImportForm
from .groups_generator import create_groups, fill_groups


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    change_list_template = 'admin/model_change_list.html'
    list_display = ('tg_username', 'name', 'level')
    list_filter = ['level']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                '^import/$',
                self.admin_site.admin_view(self.import_students),
                name='import-students'
            ),
        ]

        return custom_urls + urls

    def import_students(self, request):
        if request.method != 'POST':
            form = StudentImportForm()
        else:
            form = StudentImportForm(request.POST, request.FILES)

            if form.is_valid():
                students = form.save()

                try:
                    for student in students:
                        Student.objects.update_or_create(
                            tg_username=student['tg_username'],
                            name=student['name'],
                            level=student['level'],
                            discord_username=student.get('discord_username', None),
                            is_far_east=student.get('is_far_east', False),
                            time=student.get('time_from', None),
                        )
                except KeyError:
                    form.add_error('file_json', 'Неверный формат JSON')
                else:
                    return HttpResponseRedirect('../')

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['title'] = 'Импорт студентов'

        return TemplateResponse(
            request,
            'admin/import_form.html',
            context,
        )


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    change_list_template = 'admin/model_change_list.html'
    list_display = ('tg_username', 'name', 'time_from', 'time_to')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                '^import/$',
                self.admin_site.admin_view(self.import_managers),
                name='import-managers'
            ),
        ]

        return custom_urls + urls

    def import_managers(self, request):
        if request.method != 'POST':
            form = StudentImportForm()
        else:
            form = StudentImportForm(request.POST, request.FILES)

            if form.is_valid():
                managers = form.save()
                try:
                    for manager in managers:
                        Manager.objects.update_or_create(
                            tg_username=manager['tg_username'],
                            name=manager['name'],
                            time_from=manager['time_from'],
                            time_to=manager['time_to']
                        )
                except KeyError:
                    form.add_error('file_json', 'Неверный формат JSON')
                else:
                    return HttpResponseRedirect('../')

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['title'] = 'Импорт менеджеров'

        return TemplateResponse(
            request,
            'admin/import_form.html',
            context,
        )

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('project', 'time', 'manager', 'show_students')
    list_filter = ['project']

    def show_students(self, obj):
        return format_html('<br/>'.join([str(student) for student in obj.students.all()]))
    show_students.short_description = 'Студенты'
    show_students.allow_tags = True


class GroupsInlines(admin.TabularInline):
    model = Group
    fields = ('time', 'manager', 'show_students')
    readonly_fields = ('show_students',)


    def show_students(self, obj):
        return format_html('<br/>'.join([str(student) for student in obj.students.all()]))

    show_students.short_description = 'Студенты'
    
    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'generate_button', 'has_lonely_students')
    inlines = [GroupsInlines]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            re_path(
                r'^(?P<project_id>.+)/generate/$',
                self.admin_site.admin_view(self.generate_groups),
                name='group-generate',
            ),
        ]
        return custom_urls + urls
        

    def generate_button(self, obj):
        if obj.group_set.all():
            url = '{}?project__id__exact={}'.format(reverse('admin:automation_group_changelist'), obj.pk)

            return format_html(
                f'<a class="button" href="{url}">Смотреть группы</a>',
            );
        return format_html(
            '<a class="button" href="{}">Генерировать группы</a>',
            reverse('admin:group-generate', args=[obj.pk]),
        )
    generate_button.short_description = 'Сгенерировать группы'


    def has_lonely_students(self, obj):
        if obj.lonelystudent_set.all() and obj.group_set.all():
            url = '{}?project__id__exact={}'.format(reverse('admin:automation_lonelystudent_changelist'), obj.pk)

            return format_html(
                f'<a class="button" href="{url}">Смотреть студентов</a>',
            )

    has_lonely_students.short_description = 'Нераспределенные студенты'


    def generate_groups(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        groups = create_groups(project_id)
        levels = Student.Level.choices
        redirect_url = '{}?project__id__exact={}'.format(reverse('admin:automation_group_changelist'), project_id)
        LonelyStudent.objects.filter(project=project).delete()

        for level in levels:
            level_value = level[0]
            students = Student.objects.filter(level=level_value)
            fill_groups(groups, students)

        for lonely_student in Student.objects.all().exclude(group__project=project_id):
            LonelyStudent(
                project=project,
                student=lonely_student,
            ).save()

        return HttpResponseRedirect(redirect_url)


@admin.register(LonelyStudent)
class LonelyStudentAdmin(admin.ModelAdmin):
    list_display = ('project', 'link_to_student', 'show_student_time')
    list_filter = ['project']

    def link_to_student(self, obj):
        link = reverse("admin:automation_student_change", args=[obj.student.tg_username])
        return format_html('<a href="{}">{}</a>', link, str(obj.student))
    link_to_student.short_description = 'Студент'

    def show_student_time(self, obj):
        return obj.student.time
    show_student_time.short_description = 'Удобное время'
