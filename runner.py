"""Automated job processor/monitor.

    Model runs:
        manage_model_runners()
        Runs 4 reps, or possibly less if recently reps finished quickly

    Database maintenance & backup:
        manage_db_maintenance()
        Runs once daily, between 2am and 6am, dumping out tables to dated directory in cloud (OneDrive)

    Data status summary

    Model summary

"""
from datetime import datetime, timedelta
import numpy as np
import os
import pandas as pd
import psutil
from time import sleep

from config import dateparse, home_dir, log, pandas_format


procmon_fpath = f'{home_dir}/procmon.json'


def filter_jobs(status_df, script_name):
    df = status_df[status_df['script'] == script_name]
    running_df = df[df['status'] == 'running']
    done_df = df[df['status'] == 'done']
    return running_df, done_df


def manage_computes(status_df):
    reps = 1
    running, done = filter_jobs(status_df, 'compute.py')
    if len(done) > 0:
        last_finished_secs = (datetime.now() - dateparse(done.iloc[0].finished)).seconds
        last_elapsed = done.iloc[0].elapsed
        h, m, s = last_elapsed.split(':')
        last_elapsed_secs = int(float(h)) * 3600 + int(float(m)) * 60 + int(float(s))
        if last_finished_secs < 300:
            if last_elapsed_secs < 30:
                reps = 0
            else:
                reps = 1
        else:
            reps = 1
    count = len(running)
    log(f'Computes: {count} rep running (max {reps})')
    if count < reps:
        log(f'Launching 1 compute...')
        os.system(f'start "Blackjack compute" /min python compute.py')


def fetch_running():
    """Collect info on all relevant running processes."""
    df = pd.DataFrame(columns=['pid', 'script', 'cmd_line', 'create_time', 'memory', 'swap', 'status'])
    for p in psutil.process_iter(['pid', 'username']):
        pid = p.pid
        try:
            username = p.username()
            if username != r'JOHN-DESKTOP\John':
                continue
            proc = psutil.Process(pid)
            args = proc.cmdline()
            cmd_line = ' '.join(args).lower()
            if cmd_line.startswith('python'):
                if len(args) < 2:
                    continue
                script = args[1]
                if script == 'procmon.py':
                    continue
            else:
                continue
            attributes = proc.as_dict(['create_time', 'memory_full_info', 'status'])
            df.loc[len(df)] = [
                pid,
                script,
                cmd_line,
                attributes['create_time'],
                attributes['memory_full_info'].wset,
                attributes['memory_full_info'].pagefile,
                attributes['status']
            ]
        except (PermissionError, psutil.AccessDenied, psutil.NoSuchProcess) as e:
            continue
    df = df.set_index('pid')
    return df


def calc_cmd_line(row, running_df):
    if not pd.isna(row.cmd_line):
        return row.cmd_line
    if row.name in running_df.index:
        return running_df.loc[row.name].cmd_line
    return np.nan


def calc_finished(row, running_df):
    if not pd.isna(row.finished):
        return row.finished
    if row.name in running_df.index:
        return np.nan
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def calc_script(row, running_df):
    if not pd.isna(row.script):
        return row.script
    if row.name in running_df.index:
        return running_df.loc[row.name].script
    return np.nan


def calc_started(row, running_df):
    if not pd.isna(row.started):
        return row.started
    if row.name in running_df.index:
        secs_since_epoch = running_df.loc[row.name].create_time
        return datetime.fromtimestamp(secs_since_epoch).strftime('%Y-%m-%d %H:%M:%S')
    return np.nan


def calc_elapsed(row):
    if pd.isna(row.started):
        return np.nan
    started = dateparse(row.started)
    finished = datetime.now()
    if not pd.isna(row.finished):
        finished = dateparse(row.finished)
    elapsed = finished - started
    h = int(elapsed.seconds / 3600.0)
    m = int(elapsed.seconds / 60.0) - h * 60
    s = elapsed.seconds - h * 3600 - m * 60
    return f'{h:02}:{m:02}:{s:02}'


def job_status():
    """This iterator returns a dataframe with job status information"""
    df = load_status()
    if df is None:
        df = pd.DataFrame(columns=['pid', 'script', 'cmd_line', 'status', 'started', 'finished', 'memory', 'swap'])
    df = df.set_index('pid')
    last_save = datetime.now()
    while True:
        running_df = fetch_running()
        df = pd.concat([df, running_df[['script']]])
        df['script'] = df.apply(lambda row: calc_script(row, running_df), axis=1)
        df['cmd_line'] = df.apply(lambda row: calc_cmd_line(row, running_df), axis=1)
        df['status'] = df.apply(lambda row: running_df.loc[row.name].status if row.name in running_df.index else 'done', axis=1)
        df['started'] = df.apply(lambda row: calc_started(row, running_df), axis=1)
        df['finished'] = df.apply(lambda row: calc_finished(row, running_df), axis=1)
        df['elapsed'] = df.apply(lambda row: calc_elapsed(row), axis=1)
        df['memory'] = running_df['memory']
        df['swap'] = running_df['swap']
        df = df[~df.index.duplicated(keep='first')]
        df = df.sort_values(['status', 'finished', 'started'], ascending=[False, False, False])
        if datetime.now() > last_save + timedelta(seconds=60):
            save_status(df)
        yield df


def load_status():
    if not os.path.isfile(procmon_fpath):
        return None
    df = pd.read_json(procmon_fpath)
    return df


def save_status(df):
    df = df.reset_index()
    df = df[df['status'] == 'done']
    if len(df) == 0:
        return
    date_cutoff = (datetime.now() - timedelta(seconds=24 * 60 * 60)).strftime('%Y-%m-%d %H:%M:%S')
    df = df[df['finished'] > date_cutoff]
    if len(df) == 0:
        return
    df.to_json(procmon_fpath, orient='records', date_format='iso', indent=4)


def show_status(df):
    os.system('cls')
    df = df.drop(columns='cmd_line')
    print('')
    print(f'Job Status at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('')
    print(df[df['status'] == 'running'])
    print('')
    print(df[df['status'] == 'done'][:50])
    print('')


def main():
    log('Start...')
    pandas_format()
    for status_df in job_status():
        show_status(status_df)
        manage_computes(status_df)
        sleep(5)


if __name__ == '__main__':
    main()
