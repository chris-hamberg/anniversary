from dateutil import parser, relativedelta
from pprint import pprint
from collections import OrderedDict
import csv, datetime, json, sys

def normalize(run_date):
    '''Convert command line arg to datetime.'''
    month, day, year = tuple(map(int, run_date.split('-')))
    return datetime.datetime(year, month, day)

def input(fname):
    '''read csv, sort results by date'''
    data = list()
    with open(fname, 'r') as fhand:
        reader = csv.DictReader(fhand)
        for row in reader:
            data.append(row)
    return sorted(data, key=lambda col: col['hire_date'])

def anniversary(employee):
    '''find the first milestone for employee after RUN_DATE'''
    hire_date = employee['hire_date']
    hire_date = parser.parse(hire_date) # dateutil object
    milestone = hire_date + relativedelta.relativedelta(years=+5)
    while milestone < RUN_DATE:
        # find a milestone that isn't in the past
        milestone = milestone + relativedelta.relativedelta(years=+5)
    return milestone.strftime('%Y-%m-%d')
           
def filter(anniversaries):
    '''conform data to output specification, filter milestones to soonest 5'''
    data = list()
    for supervisor in anniversaries:
        # milestones sorted for the immediate 5 upcoming milestones
        record = {'supervisor_id': supervisor,
                  'upcoming_milestones': sorted(
                      anniversaries[supervisor], 
                      key=lambda entries: entries['anniversary_date'])[:5]
                }
        data.append(record)
    return json.dumps(data)

def output(data):
    '''find milestones, filter for the soonest 5 per supervisor'''
    # build preliminary data structure
    anniversaries = {record['supervisor_id']: [] for record in data}
    for employee in data: # raw csv
        employees_supervisor = employee['supervisor_id']
        milestone = OrderedDict({'employee_id': employee['employee_id'],
                     'anniversary_date': anniversary(employee)
                     })
        anniversaries[employees_supervisor].append(milestone)
    return filter(anniversaries) # reduce data down to specification

def main(fname):
    data = input(fname)
    result = output(data)
    pprint(result)

if __name__ == '__main__':
    try:
        fname, RUN_DATE = sys.argv[1], sys.argv[2]
    except IndexError as bad_cli_arg:
        print('usage: ~$ python anniveraries.py <file.csv> <month-day-year>')
    else:
        RUN_DATE = normalize(RUN_DATE)
        main(fname)
