import json
import os

from config import home_dir


def cleanup():
    for fname in os.listdir(f'{home_dir}/states'):
        fpath = f'{home_dir}/states/{fname}'
        if not fpath.endswith('.json'):
            continue
        with open(fpath, 'r') as fp:
            try:
                data = json.load(fp)
            except:
                print(f'ERROR: {fpath} failed to load')
                continue
        if 'valuation' not in data or data['valuation'] is None:
            continue
        max_nodes = 0
        for val in data['valuation']:
            max_nodes = max(max_nodes, val['nodes'])
        print(f'{fname}: {max_nodes} nodes')
        if max_nodes < 10000:
            os.remove(fpath)


if __name__ == '__main__':
    cleanup()
