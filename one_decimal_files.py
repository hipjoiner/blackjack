import os

from config import home_dir, log
from rules import Rules


def rename_all_files_under(true_count_dir, tc_dir):
    log(true_count_dir)
    for dirpath, dirnames, filenames in os.walk(true_count_dir):
        sub_dir = dirpath.replace('\\', '/')
        for f in filenames:
            if '.0' in f:
                continue
            fpath = f'{sub_dir}/{f}'
            tc_index = f.index(tc_dir)
            fixed = 4
            new_f = f'{f[:tc_index + fixed]}.0{f[tc_index + fixed:]}'
            new_fpath = f'{sub_dir}/{new_f}'
            log(f'{fpath:60} --> {new_fpath}')
            try:
                os.rename(fpath, new_fpath)
            except FileExistsError:
                log(f'WARNING: target exists; removing for rename: {new_fpath}')
                os.remove(new_fpath)
                os.rename(fpath, new_fpath)


def walk_tree(rules):
    base_dir = f'{home_dir}/states/{rules.implied_name}'
    tc_dirs = os.listdir(base_dir)
    for tc_dir in tc_dirs:
        if tc_dir.endswith('.0'):
            continue
        true_count_dir = f'{home_dir}/states/{rules.implied_name}/{tc_dir}'
        rename_all_files_under(true_count_dir, tc_dir)
        new_true_count_dir = f'{true_count_dir}.0'
        log(f'{true_count_dir} --> {new_true_count_dir}')
        os.rename(true_count_dir, new_true_count_dir)


if __name__ == '__main__':
    r = Rules(
        blackjack_pays=1.5,
        shoe_decks=4,
        hit_soft_17=True,
        double_allowed='Any2',
        splits_allowed=3,
        double_after_split=True,
        resplit_aces=False,
        late_surrender=True,
    )
    walk_tree(rules=r)
