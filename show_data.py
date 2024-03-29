import json
import os
import pandas as pd
import sys

from config import pandas_format
from deal import Deal
from rules import Rules


abbrev = {
    'Insurance': 'I',
    'Blackjack': 'B',
    'Surrender': 'R',
    'Split': 'Y',
    'Double': 'D',
    'Hit': 'H',
    'Stand': 'S',
    'Win': 'W',
    'Lose': 'L',
    'Push': 'P',
}

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


def choice(row, num, tag):
    if len(row.val_data) < num:
        return '-'
    data = row.val_data[num - 1]
    if tag == 'action':
        action = data.get('action', data.get('outcome'))
        # action = abbrev[action]
        return action
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
    df['ev2'] = df.apply(lambda row: row.prob * row.value2 if row.value2 != '-' else None, axis=1)
    df['action3'] = df.apply(lambda row: choice(row, 3, 'action'), axis=1)
    df['value3'] = df.apply(lambda row: choice(row, 3, 'value'), axis=1)
    df['nodes3'] = df.apply(lambda row: choice(row, 3, 'nodes'), axis=1)
    df['ev3'] = df.apply(lambda row: row.prob * row.value3 if row.value3 != '-' else None, axis=1)
    df['actions'] = df.apply(lambda row: f'{row.action1}/{row.action2}', axis=1)
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
        'actions',
    ]]
    return df


def dsort(row):
    cards_key = ''
    for c in row.state.dealer.cards:
        cards_key += sort_map[c]
    return cards_key


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
        df.at[row.pcards, row.dcards] = row[col]
    return df


def hand_distinct(row, df):
    if len(df[(df['hand_type'] == row.hand_type) & (df['hand_label'] == row.hand_label)]) > 1:
        return f'({row.pcards})'
    return '    '


def hand_label(row):
    return {
        'Pairs': row.phand.cards,
        'Soft Totals': row.phand.cards,
        'Hard Totals': str(row.phand.total),
        'Surrender': str(row.phand.total),
    }[row.hand_type.strip()]


def hand_type(row):
    if row.phand.is_pair:
        return 'Pairs      '
    elif row.phand.is_soft:
        return 'Soft Totals'
    else:
        return 'Hard Totals'


def play_action(row, col):
    section = row.hand_type.strip()
    actions = str(row[col]).split('/')
    if section == 'Pairs':
        return 'Y' if actions[0] == 'Split' else '.'
    elif section in ['Soft Totals', 'Hard Totals']:
        a1, a2 = actions[0], actions[1]
        if a1 == 'Surrender':
            a1, a2 = actions[1], None
        if a1 == 'Hit':
            return 'H'
        if a1 == 'Stand':
            return 'S'
        if a1 == 'Double':
            return 'Ds' if a2 == 'Stand' else 'Dh'
    elif section == 'Surrender':
        return 'S' if actions[0] == 'Surrender' else '.'
    else:
        raise ValueError(f'Unknown section {section}')


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


if __name__ == '__main__':
    tc = 0
    if len(sys.argv) > 1:
        tc = int(float(sys.argv[1]))
    data = collect_data(true_count=tc)
    result = format_data(data, 'value1')
    pandas_format()
    print(result)
