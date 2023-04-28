import json
import os
import pandas as pd

from config import home_dir, pandas_format
from deal import Deal


action_map = {
    'Blackjack': 'B',
    'Double': 'D',
    'Hit': 'H',
    'Lose': 'L',
    'Push': 'P',
    'Split': 'Y',
    'Stand': 'S',
    'Surrender': 'R',
}

rules_instr = (1.5, 6, False, 'Any2', 3, True, True, True)


def starting_hands():
    states = {}
    d = Deal()
    hands = []
    cd1_states = d.next_states['Deal']
    for cd1, child1 in cd1_states.items():
        p1 = child1['prob']
        for cd2, child2 in child1['state'].next_states['Deal'].items():
            p2 = child2['prob']
            for cd3, child3 in child2['state'].next_states['Deal'].items():
                p3 = child3['prob']
                for cd4, child4 in child3['state'].next_states['Deal'].items():
                    s4 = child4['state']
                    states[s4.implied_name] = s4
                    p4 = child4['prob']
                    hands.append({
                        'state_name': s4.implied_name,
                        'prob': p1 * p2 * p3 * p4,
                    })
    df = pd.DataFrame(hands)
    df = df.groupby(by='state_name', as_index=False).sum()
    df['state'] = df.apply(lambda row: states[row.state_name], axis=1)
    return df[[
        'state_name',
        'state',
        'prob',
    ]]


def val_data(row):
    d = row.state
    if not os.path.isfile(d.fpath):
        raise FileNotFoundError(d.fpath)
    with open(d.fpath, 'r') as fp:
        data = json.load(fp)
    return data['valuation']


sort_map = {
    'x': '0',
    '2': '0',
    '3': '1',
    '4': '2',
    '5': '3',
    '6': '4',
    '7': '5',
    '8': '6',
    '9': '7',
    'T': '8',
    'A': '9',
}

def psort(row):
    cards_key = ''
    for c in row.state.player.cards:
        cards_key += str(9 - int(float(sort_map[c])))
    if row.state.player.is_pair:
        return f'0-Pair {cards_key} {row.state.player.cards}'
    if row.state.player.is_soft:
        return f'1-Soft {cards_key} {row.state.player.cards}'
    else:
        return f'2-Hard {21 - row.state.player.total:2}'


def dsort(row):
    cards_key = ''
    for c in row.state.dealer.cards:
        cards_key += sort_map[c]
    return cards_key


def choice(row, num, tag):
    if len(row.val_data) < num:
        return None
    data = row.val_data[num - 1]
    if tag == 'action':
        return data.get('action', data.get('outcome'))
    return data[tag]


def do_summary():
    df = starting_hands()
    df['psort'] = df.apply(lambda row: psort(row), axis=1)
    df['dsort'] = df.apply(lambda row: dsort(row), axis=1)
    df['total'] = df.apply(lambda row: row.state.player.total, axis=1)
    df['phand'] = df.apply(lambda row: row.state.player.cards, axis=1)
    df['dhand'] = df.apply(lambda row: row.state.dealer.cards, axis=1)
    df['fpath'] = df.apply(lambda row: row.state.fpath, axis=1)
    df['val_data'] = df.apply(lambda row: val_data(row), axis=1)
    df['action1'] = df.apply(lambda row: choice(row, 1, 'action'), axis=1)
    df['value1'] = df.apply(lambda row: choice(row, 1, 'value'), axis=1)
    df['nodes1'] = df.apply(lambda row: choice(row, 1, 'nodes'), axis=1)
    df['ev1'] = df.apply(lambda row: row.prob * row.value1, axis=1)
    df['action2'] = df.apply(lambda row: choice(row, 2, 'action'), axis=1)
    df['value2'] = df.apply(lambda row: choice(row, 2, 'value'), axis=1)
    df['nodes2'] = df.apply(lambda row: choice(row, 2, 'nodes'), axis=1)
    df['ev2'] = df.apply(lambda row: row.prob * row.value2 if row.value2 is not None else None, axis=1)
    df = df.sort_values(['psort', 'dsort'])
    df = df[[
        'psort',
        'dsort',
        'state_name',
        'total',
        'phand',
        'dhand',
        'prob',
        'action1',
        'value1',
        'nodes1',
        'ev1',
        'action2',
        'value2',
        'nodes2',
        'ev2',
    ]]
    pandas_format()
    print(df)
    print(df['prob'].sum())
    df.to_excel(f'{home_dir}/analysis.xlsx', index=False)


if __name__ == '__main__':
    do_summary()

