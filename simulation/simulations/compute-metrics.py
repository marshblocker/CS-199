# Usage python3.10 ./compute-metrics.py <system_variation> <username>
#
# Note: example of system_variation is 'with-srp-itp=15-thresh--0.5' (i.e., itp = 15, threshold = -0.5)

import os
import re
from sys import argv

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LOGS_PATH = os.path.join(DIR_PATH, 'logs', argv[2], argv[1])

MEM_PATTERN = r'\[\d+\] models memory size \(bytes\): (\d+)'
PROCESSING_TIME_PATTERN = r'\[\d+\] processing time \(nanoseconds\): (\d+)'
DETECTION_TIME_PATTERN = r'\[\d+\] detection time \(days\): (\d+)'

TESTS_COUNT = 100
SENSORS_COUNT = 3


def main():
    log_files = os.listdir(LOGS_PATH)

    system_mem_size_ave = 0.0
    system_processing_time_ave = 0.0
    system_detection_time_ave = 0.0
    system_modified_fscore = 0.0

    tp_total = 0
    tn_total = 0
    fp_total = 0
    fn_total = 0

    # Counter that increases if the metric is found in a log file.
    mem_counter = 0
    processing_counter = 0
    detection_counter = 0

    for filename in log_files:
        with open(os.path.join(LOGS_PATH, filename), 'r') as f:
            content = f.read()

            test_mem_sizes = re.findall(MEM_PATTERN, content)
            if len(test_mem_sizes):
                mem_counter += 1
                test_mem_sizes = list(map(lambda x: int(x), test_mem_sizes))
                test_mem_size_ave = round(
                    sum(test_mem_sizes) / len(test_mem_sizes), 2)
                system_mem_size_ave += test_mem_size_ave

            test_processing_times = re.findall(
                PROCESSING_TIME_PATTERN, content)
            if len(test_processing_times):
                processing_counter += 1
                test_processing_times = list(
                    map(lambda x: int(x), test_processing_times))
                test_processing_time_ave = round(
                    sum(test_processing_times) / len(test_processing_times), 2)
                system_processing_time_ave += test_processing_time_ave

            test_detection_times = re.findall(DETECTION_TIME_PATTERN, content)
            if len(test_detection_times):
                detection_counter += 1
                test_detection_times = list(
                    map(lambda x: int(x), test_detection_times))
                test_detection_time_ave = round(
                    sum(test_detection_times) / len(test_detection_times), 2)
                system_detection_time_ave += test_detection_time_ave

            tp_total += len(re.findall(r'\[\d+\] \[tp\]: .*', content))
            tn_total += len(re.findall(r'\[\d+\] \[tn\]: .*', content))
            fp_total += len(re.findall(r'\[\d+\] \[fp\]: .*', content))
            fn_total += len(re.findall(r'\[\d+\] \[fn\]: .*', content))

    print('{} metrics result:'.format(argv[1]))

    if system_mem_size_ave:
        system_mem_size_ave = round(system_mem_size_ave / mem_counter, 2)
    print_metric_result('average memory consumption',
                        system_mem_size_ave, 'bytes')

    if system_processing_time_ave:
        system_processing_time_ave = round(
            system_processing_time_ave / processing_counter, 2)
        system_processing_time_ave = system_processing_time_ave
    print_metric_result('average processing time',
                        system_processing_time_ave, 'nanoseconds')

    if system_detection_time_ave:
        system_detection_time_ave = round(
            system_detection_time_ave / detection_counter, 2)
    print_metric_result('average detection time',
                        system_detection_time_ave, 'days')

    system_modified_fscore = compute_modified_fscore(
        tp_total, tn_total, fp_total, fn_total)
    print_metric_result('modified f-score', system_modified_fscore)


def compute_modified_fscore(tp_total, tn_total, fp_total, fn_total):
    base_score = TESTS_COUNT*SENSORS_COUNT
    max_score = 2*base_score

    modified_fscore = (base_score + tp_total + tn_total -
                       fp_total - fn_total) / max_score
    return round(modified_fscore, 2)


def print_metric_result(metric_name, result, units=''):
    if result == 0.0:
        print('No computed result for {} metric.'.format(metric_name))
    else:
        print('{}: {} {}'.format(metric_name, result, units))


if __name__ == '__main__':
    main()
