import json
import os
from pprint import pprint
import sys

from config import home_dir, log, log_occasional
from rules import Rules


def preserve(fpath):
    """Preserve starting hands-- the ones we really care about"""
    toks = fpath[:-5].split(' ')
    if len(toks[2]) > 4:
        return False
    if len(toks) == 4 and len(toks[3]) > 2:
        return False
    return True


def bucket(fpath):
    sizes = [100000, 1000000, 10000000]
    if not hasattr(bucket, 'buckets'):
        bucket.buckets = {}
        for s in sizes:
            bkt = f'<{s:d}'
            bucket.buckets[bkt] = {
                'threshold': s,
                'file_count': 0,
                'bytes': 0,
                'files': []
            }
        bkt = f'{max(sizes):d}+'
        bucket.buckets[bkt] = {
            'threshold': 1e20,
            'file_count': 0,
            'bytes': 0,
            'files': []
        }
    log_occasional(fpath, seconds=20)
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
        raise ValueError(f'No valuation data in {fpath}')
    max_nodes = 0
    for val in data['valuation']:
        max_nodes = max(max_nodes, val['nodes'])
    bkt = f'{max(sizes):d}+'
    for s in sizes:
        if max_nodes < s:
            bkt = f'<{s:d}'
            break
    bucket.buckets[bkt]['file_count'] += 1
    bucket.buckets[bkt]['bytes'] += num_bytes
    bucket.buckets[bkt]['files'].append(fpath)
    return bucket.buckets


def remove_files(buckets, size_threshold):
    for b in buckets.values():
        if b['threshold'] <= size_threshold:
            print()
            log(f"Deleting {b['file_count']} files ({b['bytes']} bytes) w/ fewer than {b['threshold']} nodes:")
            files = sorted(b['files'])
            for fpath in files:
                log(f'{fpath}...')
                os.remove(fpath)


def cleanup(rules, size_threshold):
    base_dir = f'{home_dir}/states/{rules.implied_name}'
    tc_dirs = os.listdir(base_dir)
    buckets = None
    for tc_dir in tc_dirs:
        true_count_dir = f'{home_dir}/states/{rules.implied_name}/{tc_dir}'
        log(true_count_dir)
        for dirpath, dirnames, filenames in os.walk(true_count_dir):
            sub_dir = dirpath.replace('\\', '/')
            for f in filenames:
                fpath = f'{sub_dir}/{f}'
                if not preserve(fpath):
                    buckets = bucket(fpath)
        for b in buckets.values():
            if b['threshold'] <= size_threshold:
                log(f"So far: delete {b['file_count']} files ({b['bytes']} bytes) w/ fewer than {b['threshold']} nodes")
    if size_threshold is not None:
        remove_files(buckets, size_threshold)
    else:
        for tag in buckets.keys():
            buckets[tag]['files'] = sorted(buckets[tag]['files'][:10])
        print()
        pprint(buckets, indent=4, width=200)


if __name__ == '__main__':
    decks = 8
    if len(sys.argv) > 1:
        decks = int(float(sys.argv[1]))
    r = Rules(
        blackjack_pays=1.5,
        shoe_decks=decks,
        hit_soft_17=True,
        double_allowed='Any2',
        splits_allowed=3,
        double_after_split=True,
        resplit_aces=False,
        late_surrender=True,
    )
    cleanup(rules=r, size_threshold=100000)
