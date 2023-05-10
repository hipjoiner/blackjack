import json
import os
from pprint import pprint
import sys

from config import home_dir, log_occasional
from rules import Rules


rules = Rules(
    blackjack_pays=1.5,
    shoe_decks=8,
    hit_soft_17=True,
    double_allowed='Any2',
    splits_allowed=3,
    double_after_split=True,
    resplit_aces=False,
    late_surrender=True,
)


def bucket(fpath):
    log_occasional(fpath)
    num_bytes = os.path.getsize(fpath)
    if not fpath.endswith('.json'):
        raise FileExistsError(f'Unexpected file: {fpath}')
    with open(fpath, 'r') as fp:
        try:
            data = json.load(fp)
        except:
            print(f'ERROR: {fpath} failed to load')
            return 'na', num_bytes
    if 'valuation' not in data or data['valuation'] is None:
        return 'na', num_bytes
    max_nodes = 0
    for val in data['valuation']:
        max_nodes = max(max_nodes, val['nodes'])
    if max_nodes < 10000:
        return '<10000', num_bytes
    if max_nodes < 100000:
        return '<100000', num_bytes
    if max_nodes < 1000000:
        return '<1000000', num_bytes
    if max_nodes < 10000000:
        return '<10000000', num_bytes
    return '10000000+', num_bytes


def cleanup(true_count):
    buckets = {
        'na': {'count': 0, 'bytes': 0},
        '<10000': {'count': 0, 'bytes': 0},
        '<100000': {'count': 0, 'bytes': 0},
        '<1000000': {'count': 0, 'bytes': 0},
        '<10000000': {'count': 0, 'bytes': 0},
        '10000000+': {'count': 0, 'bytes': 0},
    }
    base_dir = f'{home_dir}/states/{rules.implied_name}/TC{true_count}'
    for dirpath, dirnames, filenames in os.walk(base_dir):
        sub_dir = dirpath.replace('\\', '/')
        for f in filenames:
            fpath = f'{sub_dir}/{f}'
            log_occasional(fpath)
            bkt, num_bytes = bucket(fpath)
            buckets[bkt]['count'] += 1
            buckets[bkt]['bytes'] += num_bytes
    return buckets


if __name__ == '__main__':
    tc = 0
    if len(sys.argv) > 1:
        tc = int(float(sys.argv[1]))
    results = cleanup(true_count=tc)
    print()
    pprint(results, indent=4, width=10)
