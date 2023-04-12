from functools import lru_cache
import json
import os
import sys

from config import data, log
from table import Table


class State:
    """
    State engine, and focus for computation of expected value.
    The Deal will start with a single bettor hand, but the bettor may split into two or more hands.
    We compute expected value for each of the splits of course, since we are computing recursively,
        but the deal EV is the one of primary interest to us.
    """
    node_threshold = 10000

    def __init__(self, table_name, cards=''):
        self.table = Table(table_name, preset=cards)
        self.cards = cards
        while len(self.table.shoe.dealt) < len(self.table.shoe.preset):
            self.deal_card()
        self.cache = self.load()

    def deal_card(self):
        player = self.next_player
        if player is None:
            raise ValueError('Tried to deal card but no player wants a card')
        card = self.table.shoe.get_card()
        player.add_card(card)

    @property
    @lru_cache()
    def expected_value(self):
        if self.net_value is not None:
            return self.net_value
        ev = sum([idata['ev'] * idata['prob'] for iname, idata in self.next_states.items()])
        return ev

    @property
    def fpath(self):
        p = f'{data}/deals/{self.table.name}/'
        for i in range(int(len(self.cards) / 2) - 1):
            sub = self.cards[i * 2:(i + 1) * 2]
            p += f'{sub}/'
        p += f'{self.name}.json'
        return p

    @property
    def is_done(self):
        return self.next_player is None

    def load(self):
        if not os.path.isfile(self.fpath):
            return None
        with open(self.fpath, 'r') as fp:
            contents = json.load(fp)
        return contents['deal']

    @property
    def name(self):
        return f'{self.table.name}-{self.cards}'

    @property
    def net_value(self):
        return self.table.bettor.net_value

    @property
    def next_player(self):
        """Return reference to next player to play, or None if all players are done"""
        if len(self.table.bettor.hand.cards) == 0:
            return self.table.bettor
        if len(self.table.dealer.hand.cards) == 0:
            return self.table.dealer
        if len(self.table.bettor.hand.cards) == 1:
            return self.table.bettor
        if len(self.table.dealer.hand.cards) == 1:
            return self.table.dealer
        if not self.table.bettor.is_done:
            return self.table.bettor
        if not self.table.dealer.is_done:
            return self.table.dealer
        return None

    @property
    @lru_cache()
    def next_states(self):
        if self.is_done:
            return None
        if self.cache:
            log(f'Using {self.name} next_states from cache...')
            return self.cache['next_states']
        states = {}
        probs = self.table.shoe.pdf
        for name, state in self.next_states_recursive.items():
            card = name[-1]
            states[name] = {
                'prob': probs[card],
                'is_done': state.is_done,
                'net': state.net_value,
                'ev': state.expected_value,
                'nodes': state.nodes,
            }
            if state.nodes > State.node_threshold and state.cache is None:
                log(f'Writing {state.name} ({state.nodes} nodes) to cache...')
                state.save()
        return states

    @property
    @lru_cache()
    def next_states_recursive(self):
        states = {}
        for card, prob in self.table.shoe.pdf.items():
            state = State(self.table.name, cards=f'{self.cards}{card}')
            states[state.name] = state
        return states

    @property
    @lru_cache()
    def nodes(self):
        if self.net_value is not None:
            return 1
        return sum([idata['nodes'] for iname, idata in self.next_states.items()]) + 1

    def save(self):
        info = self.state   # Make sure it computes before creating dirs & opening files
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
        with open(self.fpath, 'w') as fp:
            json.dump(info, fp, indent=4)

    @property
    def state(self):
        return {
            'deal': {
                'name': self.name,
                'is_done': self.is_done,
                'net_value': self.net_value,
                'expected_value': self.expected_value,
                'nodes': self.nodes,
                'next_states': self.next_states,
            },
            'table': self.table.state,
            'shoe': self.table.shoe.state,
            # 'rules': self.table.rules.state,
            'dealer': self.table.dealer.state,
            'bettor': self.table.bettor.state,
        }


if __name__ == '__main__':
    # d = Deal('Table1', '878A3T6')
    # d = Deal('Table1', '878A3T')
    # d = Deal('Table1', 'TAAAAA26A7')          # Bug fix: player's blackjack means dealer takes no cards
    # d = Deal('Table1', '878A3T822AAAA283AA2922AA29')
    # d = Deal('Table1', 'TT5T')                # Bug fix: bettor's 15 surrenders to T regardless of future cards
    # d = Deal('Table1', 'TA2AAAAAAAA35AAA3')   # OK
    # d = Deal('Table1', '')
    t = 'Table1'
    c = ''
    if len(sys.argv) > 1:
        t = sys.argv[1]
        if len(sys.argv) > 2:
            c = sys.argv[2]
    d = State(t, c)
    d.save()
