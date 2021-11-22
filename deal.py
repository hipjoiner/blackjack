from datetime import datetime, timedelta
import json
import os
from pprint import pprint

from config import data
from table import Table


def log(txt):
    now = datetime.now()
    if not hasattr(log, 'next'):
        log.next = now
        log.count = 0
    log.count += 1
    if datetime.now() >= log.next:
        print(f'{now.strftime("%Y-%m-%d %H:%M:%S")} ({log.count}) {txt}')
        log.next = now + timedelta(seconds=5)


class Deal:
    """
    State engine, and focus for computation of expected value.
    The Deal will start with a single bettor hand, but the bettor may split into two or more hands.
    We compute expected value for each of the splits of course, since we are computing recursively,
        but the deal EV is the one of primary interest to us.
    """
    def __init__(self, table_name, cards=''):
        self.table = Table(table_name, preset=cards)
        self.cards = cards
        log(f'Instantiating {self.name}...')
        while len(self.table.shoe.dealt) < len(self.table.shoe.preset):
            self.deal_card()

    def deal_card(self):
        player = self.next_player
        if player is None:
            raise ValueError('Tried to deal card but no player wants a card')
        player.add_card(self.table.shoe.get_card())

    @property
    def expected_value(self):
        if self.net_value is not None:
            ev = self.net_value
            nodes = 1
        else:
            # Recursive
            ev = 0.0
            nodes = 0
            for name, state_data in self.next_states.items():
                istate = state_data['state']
                iev, inodes = istate.expected_value
                ev += iev * state_data['prob']
                nodes += inodes
                if nodes >= 10:
                    istate.save()
        return ev, nodes

    @property
    def fpath(self):
        os.makedirs(f'{data}/deals/{self.table.name}', exist_ok=True)
        return f'{data}/deals/{self.table.name}/{self.name}.json'

    @property
    def is_done(self):
        return self.next_player is None

    @property
    def name(self):
        return f'{self.table.name}-{self.cards}'

    @property
    def net_value(self):
        return self.table.bettor.net_value

    @property
    def next_player(self):
        """Return reference to next player to play, or None if all players are done"""
        if len(self.table.bettor.hands[0].cards) == 0:
            return self.table.bettor
        if len(self.table.dealer.hands[0].cards) == 0:
            return self.table.dealer
        if len(self.table.bettor.hands[0].cards) == 1:
            return self.table.bettor
        if len(self.table.dealer.hands[0].cards) == 1:
            return self.table.dealer
        if not self.table.bettor.is_done:
            return self.table.bettor
        if not self.table.dealer.is_done:
            return self.table.dealer
        return None

    @property
    def next_states(self):
        if self.is_done:
            return None
        states = {}
        for card, prob in self.table.shoe.pdf.items():
            name = f'{self.name}{card}'
            state = Deal(self.table.name, cards=f'{self.cards}{card}')
            states[name] = {
                'prob': prob,
                'state': state,
            }
        return states

    @property
    def next_state_info(self):
        state_info = {}
        states = self.next_states
        if states:
            for name, data in states.items():
                ev, nodes = data['state'].expected_value
                state_info[name] = {
                    'probability': data['prob'],
                    'is_done': data['state'].is_done,
                    'net_value': data['state'].net_value,
                    'expected_value': ev,
                    'nodes': nodes
                }
        return state_info

    @property
    def state(self):
        ev, nodes = self.expected_value
        return {
            'deal': {
                'name': self.name,
                'is_done': self.is_done,
                'net_value': self.net_value,
                'expected_value': ev,
                'nodes': nodes,
                'next_states': self.next_state_info,
            },
            'table': self.table.state,
            'shoe': self.table.shoe.state,
            # 'rules': self.table.rules.state,
            'dealer': self.table.dealer.state,
            'bettor': self.table.bettor.state,
        }

    def save(self):
        with open(self.fpath, 'w') as fp:
            json.dump(self.state, fp, indent=4)


if __name__ == '__main__':
    d = Deal('Table1', '878A3T6')
    # d = Deal('Table1', '878A3T')
    # d = Deal('Table1', '878A3T822AAAA283AA2922AA29')
    # print('')
    # pprint(d.state)
    d.save()
    # x = d.expected_value
