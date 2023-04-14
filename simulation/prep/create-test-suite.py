# This creates test suite

from datetime import datetime, timedelta
from random import randint, sample

START_DATE = datetime(2012, 1, 1)
END_DATE = datetime(2021, 12, 31)
TOTAL_DAYS = (END_DATE - START_DATE).days + 1

# Equivalent to maximum trust points
MIN_ATTACK_PERIOD = 30

STATION_NAMES = ["Port Area", "Sangley Point", "Science Garden"]

def main():
    test_suite = get_test_suite()
    check_test_suite_validity(test_suite)
    latex = get_latex_table_of_test_suite(test_suite)
    print(latex)

# 10 test cases with no attacked sensors
# 30 test cases with 1 attacked sensor
# 30 test cases with 2 attacked sensors
# 30 test cases with 3 attacked sensors
# Date of attack and period of attack of is randomized
def get_test_suite():
    test_suite = []

    for _ in range(10):
        test_suite.append({
            "Port Area": {},
            "Sangley Point": {},
            "Science Garden": {}
        })

    for _ in range(30):
        sensors_dict = get_sensors_dict(1)
        test_suite.append(sensors_dict)

    for _ in range(30):
        sensors_dict = get_sensors_dict(2)
        test_suite.append(sensors_dict)

    for _ in range(30):
        sensors_dict = get_sensors_dict(3)
        test_suite.append(sensors_dict)

    return test_suite

def get_random_attack_date() -> int:
    # The random_attack_date must be enough to accommodate the MIN_ATTACK_PERIOD
    random_attack_date = randint(1, TOTAL_DAYS - MIN_ATTACK_PERIOD + 1)
    return random_attack_date


def get_random_attack_period(attack_date: int) -> int:
    random_attack_period = randint(1, TOTAL_DAYS - attack_date - 1)
    return random_attack_period

def get_sensors_dict(k: int):
    attacked_sensors = sample(STATION_NAMES, k=k)
    attacked_sensors_dict = {}

    for sensor_name in attacked_sensors:
        random_attack_date = get_random_attack_date()
        random_attack_period = get_random_attack_period(random_attack_date)

        random_attack_date = START_DATE + timedelta(random_attack_date - 1)

        attacked_sensors_dict[sensor_name] = {
            "attack_date": random_attack_date,
            "attack_period": random_attack_period
        }

    safe_sensors = filter(
        lambda x: not x in attacked_sensors, STATION_NAMES)
    safe_sensors_dict = {
        sensor_name: {} for sensor_name in safe_sensors
    }

    return attacked_sensors_dict | safe_sensors_dict

def check_test_suite_validity(test_suite):
    for test_case in test_suite:
        for station in test_case:
            attack_info = test_case[station]
            if len(attack_info):
                attack_date = attack_info["attack_date"]
                attack_period = attack_info["attack_period"]

                assert attack_date + timedelta(attack_period - 1) <= END_DATE

def get_station_latex(station, test_case):
    line = ''
    station_info = test_case[station]

    if not len(station_info):
        line += '& None & None '
    else:
        attack_date = station_info['attack_date'].strftime("%b %d, %Y")
        attack_period = station_info['attack_period']

        line += '& {} & {} '.format(attack_date, attack_period) 

    return line


def get_latex_table_of_test_suite(test_suite):
    latex_start = '''
    \\begin{table}[!ht]
        \\centering
        \\tabcolsep=0.11cm
        \\scalebox{0.8}{
            \\begin{tabular}{|*{7}{c|}}
                \\cline{2-7}
                \\multicolumn{1}{c|}{} & \\multicolumn{2}{c}{\\textbf{Port Area Station}} & \\multicolumn{2}{|c}{\\textbf{Sangley Point Station}} & \\multicolumn{2}{|c|}{\\textbf{Science Garden Station}} \\\\ \\hline
                \\textbf{Test Case} & \\textbf{Attack Date} & \\textbf{Attack Period} & \\textbf{Attack Date} & \\textbf{Attack Period} & \\textbf{Attack Date} & \\textbf{Attack Period} \\\\ \\hline
'''

    latex_end = '''
            \\end{tabular}
        }
        \\caption{Test Matrices. (Attack Period is in days unit)}
    \\end{table}
    '''

    latex_mid = ''

    for i, test_case in enumerate(test_suite):
        line = '                    '
        line += '{} '.format(i+1)
        line += get_station_latex("Port Area", test_case)
        line += get_station_latex("Sangley Point", test_case)
        line += get_station_latex("Science Garden", test_case)
        line += '\\\\ \\hline \n'

        latex_mid += line

    return latex_start + latex_mid + latex_end

if __name__ == '__main__':
    main()