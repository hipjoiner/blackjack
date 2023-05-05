import json
import os
import pandas as pd

from config import home_dir, pandas_format
from deal import Deal
from hand import Hand
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


def starting_hands(true_count=0):
    """Return dataframe of starting hand states (Deal objects) along with probability of each."""
    states = {}
    d = Deal(rules=rules.instreams, true_count=true_count)
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


def collect_data(true_count=0):
    df = starting_hands(true_count=true_count)
    df['psort'] = df.apply(lambda row: psort(row), axis=1)
    df['dsort'] = df.apply(lambda row: dsort(row), axis=1)
    df['total'] = df.apply(lambda row: row.state.player.total, axis=1)
    df['phand'] = df.apply(lambda row: row.state.player, axis=1)
    df['pcards'] = df.apply(lambda row: row.state.player.cards, axis=1)
    df['dhand'] = df.apply(lambda row: row.state.dealer, axis=1)
    df['dcards'] = df.apply(lambda row: row.state.dealer.cards, axis=1)
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
    df['action3'] = df.apply(lambda row: choice(row, 3, 'action'), axis=1)
    df['value3'] = df.apply(lambda row: choice(row, 3, 'value'), axis=1)
    df['nodes3'] = df.apply(lambda row: choice(row, 3, 'nodes'), axis=1)
    df['ev3'] = df.apply(lambda row: row.prob * row.value3 if row.value3 is not None else None, axis=1)
    df = df.sort_values(['psort', 'dsort'])
    df = df[[
        'psort',
        'dsort',
        'state_name',
        'total',
        'phand',
        'pcards',
        'dhand',
        'dcards',
        'prob',
        'action1',
        'value1',
        'nodes1',
        'ev1',
        'action2',
        'value2',
        'nodes2',
        'ev2',
        'action3',
        'value3',
        'nodes3',
        'ev3',
    ]]
    # df.to_excel(f'{home_dir}/analysis TC{tc:+d}.xlsx', index=False)
    return df


def hand_type(row):
    if row.phand.is_pair:
        return 'Pair'
    if row.phand.is_soft:
        return 'Soft'
    return 'Hard'


def hand_label(row):
    if row.hand_type in ['Pair', 'Soft']:
        return row.phand.cards
    return str(row.phand.total)


def format_data(data_df, col):
    cols = ['hand_type', 'phand', 'pcards', 'hand_label']
    cols.extend(data_df['dcards'].drop_duplicates(ignore_index=True).to_list())
    df = pd.DataFrame(columns=cols)
    df['phand'] = data_df['phand']
    df['pcards'] = data_df['pcards']
    df = df.drop_duplicates(subset=['pcards'])
    df['hand_type'] = df.apply(lambda row: hand_type(row), axis=1)
    df['hand_label'] = df.apply(lambda row: hand_label(row), axis=1)
    df = df.set_index('pcards')
    # Fill lattice from rows of data_df
    for i, row in data_df.iterrows():
        # print(f'{i}: {row}')
        df.at[row.pcards, row.dcards] = row[col]
    return df


if __name__ == '__main__':
    tc = 0
    data = collect_data(true_count=tc)
    # print(f"Probability checksum: {result['prob'].sum()}")
    # result = format_data(result, 'action1')
    result = format_data(data, 'ev1')
    # result = format_data(data, 'value1')
    pandas_format()
    print(result)
    result.to_excel(f'{home_dir}/summary TC{tc:+d}.xlsx', index=False)
