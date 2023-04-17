# Usage: python3.10 ./compute-avg-retraining.py <sys_type>
# 
# Note: example of sys_type is 'with-srp-15'.

import os
import re
from sys import argv

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LOGS_PATH = os.path.join(DIR_PATH, '..', 'logs', argv[1])

avg_retraining = 0.0
counter = 0
for filename in os.listdir(LOGS_PATH):
    with open(os.path.join(LOGS_PATH, filename), 'r') as f:
        avg_retraining += int(re.findall(r'Number of retraining: (\d+)', f.read())[0])
        counter += 1

print('average retraining: {}'.format(round(avg_retraining / counter, 2)))