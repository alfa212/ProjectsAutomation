import datetime as dt

from .models import Manager, Group, Student, Project


def create_groups(project_id):
    groups = []
    project = Project.objects.get(pk=project_id)

    for manager in Manager.objects.all():
        time_from = manager.time_from
        time_to = manager.time_to
        delta = dt.datetime.combine(dt.date(1, 1, 1), time_to) - dt.datetime.combine(dt.date(1, 1, 1), time_from)
        periods = delta.seconds // 3600 * 60 // 30
        
        for _ in range(1, periods + 1):
            time_period_to = (dt.datetime.combine(dt.date(1, 1, 1), time_from) + dt.timedelta(minutes=30)).time()
            group = Group(
                project=project,
                manager=manager,
                time=time_from
            )
            group.save()
            groups.append(group)
            time_from = time_period_to
    return groups


def fill_groups(groups, students):
    for group in groups:
        time_from = dt.datetime.combine(dt.date(1, 1, 1), group.time)
        time_to = time_from + dt.timedelta(minutes=30)
        for student in students:
            has_group = bool(student.group_set.filter(project=group.project.pk))
            student_time_from = dt.datetime.combine(dt.date(1, 1, 1), student.time)
            student_time_to = student_time_from + dt.timedelta(minutes=30)
            if not group.students.all():
                if not has_group and (
                        len(group.students.all()) < 3) and (
                        time_from >= student_time_from) and (
                            time_to <= student_time_to
                        ):
                    group.students.add(student)
            if not has_group and (
                    len(group.students.all()) < 3) and (
                    time_from >= student_time_from) and (
                        time_to <= student_time_to
                    ) and (
                    group.students.all()[0].level == student.level):
                group.students.add(student)

        group.save()


def get_ungrouped_students(project_id):
    return Student.objects.all().exclude(group__project=project_id)
