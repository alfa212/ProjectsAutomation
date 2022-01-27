import json
import re
import datetime as dt
from pprint import pprint

def get_time_from_message(message):
    time_periods = re.findall(r'\d+[\s]?[\D\W]?[\s]?\d+', message)
    if time_periods:
        for time in time_periods:
            if len(time) == 2:
                priority_time = dt.datetime.strptime(f'{time}:00', '%H:%M').time()
            elif ':' in time:
                time_from = dt.datetime.strptime(time, '%H:%M').time()
                delta = dt.timedelta(minutes=30)
                time_to = (dt.datetime.combine(dt.date(1, 1, 1), time_from)+ delta).time()
                priority_time = time_from, time_to
            elif '-' in time:
                split_time = time.split('-')
                time_from = dt.datetime.strptime(f'{split_time[0].strip()}:00', '%H:%M').time()
                time_to = dt.datetime.strptime(f'{split_time[-1].strip()}:00', '%H:%M').time()
                priority_time = time_from, time_to
            return priority_time
    return dt.time(8,0), dt.time(21,0)


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
        time_from = student['time_from']
        time_to = student['time_to']
        all_students[f'{name}'] = {
            'level': level,
            'tg_username': tg_username,
            'discord_username': discord_username,
            'is_far_east': is_far_east,
            'time_from': time_from,
            'time_to': time_to,
            'grouped' : False,
        }
    return all_students


def get_managers(file):
    with open(file, 'r') as fin:
        managers= json.load(fin)
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
    for manager_name, manager_work_details in managers.items():
        time_from = manager_work_details['time_from']
        time_to = manager_work_details['time_to']
        tg_username = manager_work_details['tg_username']
        delta = dt.datetime.combine(dt.date(1, 1, 1), time_to) - dt.datetime.combine(dt.date(1, 1, 1), time_from)
        periods = delta.seconds // 3600 * 60 // 30
        groups = {}
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



def main():
    students_file = 'students.json'
    managers_file = 'managers.json'
    students = get_students(students_file)
    managers = get_managers(managers_file)
    groups = create_groups(managers)


if __name__ == '__main__':
    main()    
