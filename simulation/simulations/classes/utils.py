from time import time_ns


def LOG(name: str, data: object, test_case_number='', units=''):
    match (test_case_number, units):
        case ('', ''): print('{}: {}'.format(name, data))
        case (n, ''): print('[{}] {}: {}'.format(n, name, data))
        case ('', u): print('{} ({}): {}'.format(name, u, data))
        case (n, u): print('[{}] {} ({}): {}'.format(n, name, u, data))


def LOG_DUR(action: str, started_at: int):
    ended_at = time_ns()
    duration = ended_at - started_at

    print('Time it takes to {} (nanoseconds): {}'.format(action, duration))
