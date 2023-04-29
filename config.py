from datetime import datetime, date, timedelta
import gc
import pandas as pd


home_dir = 'C:/Users/John/blackjack'
card_symbols = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A', 'x']
card_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 0]
card_indexes = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'A': 9, 'x': 10}


def dateparse(dt_str, on_error='fail'):
    """Parse dt_str to return a valid datetime.

        If dt_str is a datetime, it is returned as-is, EXCEPT for NaT which is treated here as an error.
        If dt_str is a date, it is converted to datetime.

        If any error: raise an exception, unless on_error has been set, in which case return that value.
    """
    if dt_str in [pd.NaT]:
        pass
    elif isinstance(dt_str, date):
        return datetime(dt_str.year, dt_str.month, dt_str.day)
    elif isinstance(dt_str, datetime):
        return dt_str
    else:
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
        ]
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except:
                pass
    if on_error == 'fail':
        raise ValueError(f"Failed to parse date string '{dt_str}'")
    return on_error


def log(txt):
    now = datetime.now()
    print(f'{now.strftime("%Y-%m-%d %H:%M:%S")} {txt}')


def log_occasional(txt, seconds=3):
    now = datetime.now()
    if not hasattr(log_occasional, 'last_time'):
        log_occasional.last_time = now - timedelta(days=1)
    if now > log_occasional.last_time + timedelta(seconds=seconds):
        log(txt)
        log_occasional.last_time = now


def pandas_format():
    pd.options.display.max_columns = 999
    pd.options.display.max_colwidth = 999
    pd.options.display.max_rows = 9999
    pd.options.display.width = 9999


def show_deal_refs(d=None):
    from deal import Deal
    gc.collect()
    objs = gc.get_objects()
    for i, o in enumerate(objs):
        if not isinstance(o, Deal):
            continue
        if d is not None and o != d:
            continue
        log(f'Object {i + 1}:')
        print(o)
        for j, ref in enumerate(gc.get_referrers(o)):
            log(f'  Ref {j + 1}: {str(ref)}')
            # print(ref)
