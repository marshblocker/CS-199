# Usage python3.10 ./compute-metrics.py <system_variation>
#
# Note: example of system_variation is 'with-srp-15'

import os
import re
from sys import argv

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LOGS_PATH = os.path.join(DIR_PATH, 'logs', argv[1])

MEM_PATTERN = r'\[\d+\] models memory size \(bytes\): (\d+)'
PROCESSING_TIME_PATTERN = r'\[\d+\] processing time \(nanoseconds\): (\d+)'
DETECTION_TIME_PATTERN = r'\[\d+\] detection time \(days\): (\d+)'


def main():
    log_files = os.listdir(LOGS_PATH)

    system_mem_size_ave = 0.0
    system_processing_time_ave = 0.0
    system_detection_time_ave = 0.0
    system_fscore_ave = 0.0

    # Counter that increases if the metric is found in a log file.
    mem_counter = 0
    processing_counter = 0
    detection_counter = 0
    fscore_counter = 0

    for filename in log_files:
        with open(os.path.join(LOGS_PATH, filename), 'r') as f:
            content = f.read()

            test_mem_sizes = re.findall(MEM_PATTERN, content)
            if len(test_mem_sizes):
                mem_counter += 1
                test_mem_sizes = list(map(lambda x: int(x), test_mem_sizes))
                test_mem_size_ave = round(sum(test_mem_sizes) / len(test_mem_sizes), 2)
                system_mem_size_ave += test_mem_size_ave

            test_processing_times = re.findall(PROCESSING_TIME_PATTERN, content)
            if len(test_processing_times):
                processing_counter += 1
                test_processing_times = list(map(lambda x: int(x), test_processing_times))
                test_processing_time_ave = round(sum(test_processing_times) / len(test_processing_times), 2)
                system_processing_time_ave += test_processing_time_ave

            test_detection_times = re.findall(DETECTION_TIME_PATTERN, content)
            if len(test_detection_times):
                detection_counter += 1
                test_detection_times = list(map(lambda x: int(x), test_detection_times))
                test_detection_time_ave = round(sum(test_detection_times) / len(test_detection_times), 2)
                system_detection_time_ave += test_detection_time_ave

            tp = len(re.findall(r'\[\d+\] (tp)', content))
            tn = len(re.findall(r'\[\d+\] (tn)', content))
            fp = len(re.findall(r'\[\d+\] (fp)', content))
            fn = len(re.findall(r'\[\d+\] (fn)', content))

            if tp + tn + fp + fn:
                fscore_counter += 1
                test_fscore = tp / (tp + 0.5*(fp + fn))
                system_fscore_ave += test_fscore

    print('{} metrics result:'.format(argv[1]))

    if system_mem_size_ave:
        system_mem_size_ave = round(system_mem_size_ave / mem_counter, 2)
    print_metric_result('average memory consumption', system_mem_size_ave, 'bytes')

    if system_processing_time_ave:
        system_processing_time_ave = round(system_processing_time_ave / processing_counter, 2)
        system_processing_time_ave = system_processing_time_ave / 1e+9
    print_metric_result('average processing time', system_processing_time_ave, 'seconds')

    if system_detection_time_ave:
        system_detection_time_ave = round(system_detection_time_ave / detection_counter, 2)
    print_metric_result('average detection time', system_detection_time_ave, 'days')

    if system_fscore_ave:
        system_fscore_ave = round(system_fscore_ave / fscore_counter, 2)
    print_metric_result('average f-score', system_fscore_ave)

def print_metric_result(metric_name, result, units=''):
    if result == 0.0:
        print('No computed result for {} metric.'.format(metric_name))
    else:
        print('{}: {} {}'.format(metric_name, result, units))

if __name__ == '__main__':
    main()
