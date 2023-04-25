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


def player_starts():
    starts = []
    for pc1_index in range(10):
        for pc2_index in range(10):
            plr_cds = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            plr_cds[pc1_index] += 1
            plr_cds[pc2_index] += 1
            starts.append((tuple(plr_cds), False, '', 0, False, False))
    return starts


def dealer_starts():
    starts = []
    for dealer_card_index in range(10):
        # FIXME: This doesn't include dealer Blackjack hands
        dlr_cds = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        dlr_cds[dealer_card_index] += 1
        starts.append((tuple(dlr_cds), False, '', 0, False, False))
    starts.append(((0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0), False, '', 0, False, False))
    return starts


def do_summary():
    df = pd.DataFrame(columns=[
        'player_hand',
        'dealer_hand',
        'player_hand_type',
        'player_total',
        'action_1',
        'value_1',
        'nodes_1',
        'action_2',
        'value_2',
        'nodes_2',
    ])
    df = df.set_index(['player_hand', 'dealer_hand'])

    for pinstr in player_starts():
        for dinstr in dealer_starts():
            d = Deal(rules=rules_instr, dealer=dinstr, player=pinstr)

            if not os.path.isfile(d.fpath):
                raise FileNotFoundError(d.fpath)
            with open(d.fpath, 'r') as fp:
                data = json.load(fp)
            # print(f"{d.dealer.cards} vs {d.player.cards}:")
            datum = data['valuation'][0]
            action = datum.get('action', datum.get('outcome'))
            val = datum['value']
            hand_type = 'Hard'
            if d.player.is_pair:
                hand_type = 'Pair'
            elif d.player.is_soft:
                hand_type = 'Soft'
            nodes = datum['nodes']
            index = (d.player.cards, d.dealer.cards)
            df.at[index, 'player_hand_type'] = hand_type
            df.at[index, 'player_total'] = d.player.total
            df.at[index, 'action_1'] = action
            df.at[index, 'value_1'] = val
            df.at[index, 'nodes_1'] = nodes
            if len(data['valuation']) > 1:
                datum = data['valuation'][1]
                action = datum.get('action', datum.get('outcome'))
                val = datum['value']
                nodes = datum['nodes']
                df.at[index, 'action_2'] = action
                df.at[index, 'value_2'] = val
                df.at[index, 'nodes_2'] = nodes
    pandas_format()
    df = df.reset_index(drop=False)
    print(df)
    df.to_excel(f'{home_dir}/analysis.xlsx', index=False)


if __name__ == '__main__':
    do_summary()

