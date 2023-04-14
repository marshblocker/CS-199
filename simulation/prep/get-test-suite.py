# This writes the raw test suite text from SRC as a JSON object to TARGET.

import json
import os
import re

DIR = os.path.dirname(os.path.realpath(__file__))
SRC = os.path.join(DIR, 'test-raw.txt')
TARGET = os.path.join(DIR, '..', 'test-suite.json')
PATTERN = '(?P<test_case>\d+) & (?P<port_atk_date>None|\w{3} \d{2}, \d{4}) & (?P<port_atk_drtn>None|\d+) & (?P<sley_atk_date>None|\w{3} \d{2}, \d{4}) & (?P<sley_atk_drtn>None|\d+) & (?P<scig_atk_date>None|\w{3} \d{2}, \d{4}) & (?P<scig_atk_drtn>None|\d+)'

with open(SRC, 'r') as f_src:
    lines = f_src.read().splitlines()
    test_cases = {}

    for line in lines:
        res = re.match(PATTERN, line)

        if res is None:
            raise ValueError('Pattern not matched in {}'.format(line))
        
        res = res.groupdict()
        test_cases[res['test_case']] = {
            'Port Area Sensor': {
                'atk_date': res['port_atk_date'],
                'atk_drtn': res['port_atk_drtn']
            },
            'Sangley Point Sensor': {
                'atk_date': res['sley_atk_date'],
                'atk_drtn': res['sley_atk_drtn']
            },
            'Science Garden Sensor': {
                'atk_date': res['scig_atk_date'],
                'atk_drtn': res['scig_atk_drtn']
            }
        }

    with open(TARGET, 'w') as f_target:
        json.dump(test_cases, f_target, indent=4)

