from datetime import datetime, timedelta
import gc
import pandas as pd


home_dir = 'C:/Users/John/blackjack'
card_symbols = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A', 'x']
card_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 0]
card_indexes = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'A': 9, 'x': 10}


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


def show_deal_refs():
    from deal import Deal
    gc.collect()
    objs = gc.get_objects()
    for i, o in enumerate(objs):
        if not isinstance(o, Deal):
            continue
        log(f'Object {i + 1}:')
        print(o)
        for j, ref in enumerate(gc.get_referrers(o)):
            log(f'  Ref {j + 1}: {str(ref)[:200]}')
            # print(ref)
