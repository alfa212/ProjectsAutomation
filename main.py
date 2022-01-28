import json
import re
import datetime as dt
from pprint import pprint


def get_time_from_message(message):
    time_periods = re.findall(r'\d+[\s]?[\D\W]?[\s]?\d+', message)
    priority_time = (dt.time(8, 0), dt.time(21, 0))
    if time_periods:
        for time in time_periods:
            if len(time) == 2:
                priority_time = dt.datetime.strptime(f'{time}:00', '%H:%M').time()
            elif ':' in time:
                time_from = dt.datetime.strptime(time, '%H:%M').time()
                delta = dt.timedelta(minutes=30)
                time_to = (dt.datetime.combine(dt.date(1, 1, 1), time_from) + delta).time()
                priority_time = time_from, time_to
            elif '-' in time:
                split_time = time.split('-')
                time_from = dt.datetime.strptime(f'{split_time[0].strip()}:00', '%H:%M').time()
                time_to = dt.datetime.strptime(f'{split_time[-1].strip()}:00', '%H:%M').time()
                priority_time = time_from, time_to
    return priority_time


def get_students(file):
    with open(file, 'r', encoding='utf-8') as fin:
        students = json.load(fin)
    all_students = {}
    for student in students:
        name = student['name']
        level = student['level']
        tg_username = student['tg_username']
        discord_username = student['discord_username']
        is_far_east = student['is_far_east']
        time_from = dt.datetime.strptime(student['time_from'], '%H:%M').time()
        time_to = dt.datetime.strptime(student['time_to'], '%H:%M').time()
        all_students[f'{name}'] = {
            'level': level,
            'tg_username': tg_username,
            'discord_username': discord_username,
            'is_far_east': is_far_east,
            'time_from': time_from,
            'time_to': time_to,
            'grouped': False,
        }
    return all_students


def get_managers(file):
    with open(file, 'r') as fin:
        managers = json.load(fin)
    product_managers = {}
    for manager in managers:
        name = manager['name']
        tg_username = manager['tg_username']
        time_from = dt.datetime.strptime(manager['time_from'], '%H:%M').time()
        time_to = dt.datetime.strptime(manager['time_to'], '%H:%M').time() 
        product_managers[f'{name}'] = {
            'tg_username': tg_username,
            'time_from': time_from,
            'time_to': time_to,
        }
    return product_managers


def create_groups(managers):
    groups = {}
    for manager_name, manager_work_details in managers.items():
        time_from = manager_work_details['time_from']
        time_to = manager_work_details['time_to']
        tg_username = manager_work_details['tg_username']
        delta = dt.datetime.combine(dt.date(1, 1, 1), time_to) - dt.datetime.combine(dt.date(1, 1, 1), time_from)
        periods = delta.seconds // 3600 * 60 // 30
        for period in range(1, periods + 1):
            time_period_to = (dt.datetime.combine(dt.date(1, 1, 1), time_from) + dt.timedelta(minutes=30)).time()
            groups[f'{manager_name}_{period}'] = {
                'product_manager': tg_username,
                'time_from': time_from,
                'time_to': time_period_to,
                'group': []
            }
            time_from = time_period_to
    return groups


def get_students_level(students):
    novice_students = []
    novice_plus_students = []
    junior_students = []
    for students_details in students.values():
        if students_details['level'] == 'novice':
            novice_students.append(students_details)
        elif students_details['level'] == 'novice+':
            novice_plus_students.append(students_details)
        junior_students.append(students_details)
    return novice_students, novice_plus_students, junior_students


def fill_groups(students_level, groups):
    for group_details in groups.values():
        for student in students_level:
            if len(group_details['group']) == 0:
                if not student['grouped'] and (
                        len(group_details['group']) < 3) and (
                        group_details['time_from'] == student['time_from']):
                    group_details['group'].append(student)
                    student['grouped'] = True
            if not student['grouped'] and (
                    len(group_details['group']) < 3) and (
                    group_details['time_from'] == student['time_from']) and (
                    group_details['group'][0]['level'] == student['level']):
                group_details['group'].append(student)
                student['grouped'] = True


def main():
    students_file = 'students.json'
    managers_file = 'managers.json'
    students = get_students(students_file)
    managers = get_managers(managers_file)
    groups = create_groups(managers)
    for students_level in get_students_level(students):
        fill_groups(students_level, groups)
    pprint(groups)


if __name__ == '__main__':
    main()    
