import json
import os

from config import home_dir
from rules import Rules
from shoe import Shoe
from player import Player


class Deal:
    def __init__(self, rules=None, dealer=None, player=None):
        self.rules = rules
        if self.rules is None:
            self.rules = Rules()
        self.dealer = dealer
        if self.dealer is None:
            self.dealer = Player(self.rules, is_dealer=True)
        self.player = player
        if self.player is None:
            self.player = Player(self.rules, is_dealer=False)
        self.shoe = Shoe(self.rules.decks)

    def __repr__(self):
        return self.name

    @property
    def fpath(self):
        p = f'{home_dir}/states/{self.name}.json'
        return p

    def load(self):
        if not os.path.isfile(self.fpath):
            return None
        with open(self.fpath, 'r') as fp:
            contents = json.load(fp)
        return contents['deal']

    @property
    def name(self):
        return f'{self.rules} # {self.dealer} # {self.player}'

    @property
    def next_player(self):
        # Initial deal
        for num_cards in [0, 1]:
            for p in [self.player, self.dealer]:
                if p.hand.num_cards == num_cards:
                    return p
        return None

    @property
    def next_player_symbol(self):
        if self.next_player is None:
            return None
        return self.next_player.symbol

    @property
    def next_hand(self):
        if self.next_player is None:
            return None
        if self.next_player.next_hand is None:
            return None
        return self.next_player.next_hand

    @property
    def next_hand_index(self):
        if self.next_hand is None:
            return None
        return self.next_hand.index

    @property
    def next_hand_options(self):
        if self.next_hand is None:
            return None
        return self.next_hand.options

    @property
    def next_states(self):
        if self.next_hand_options is None:
            return None
        states = {}
        for opt in self.next_hand_options:
            opt_states = {}
            if opt == 'Deal':
                for c, p in self.shoe.pdf.items():
                    nh = self.next_hand.new_state(card=c)
                    opt_states[c] = {
                        'state': nh.name,
                        'prob': p,
                    }
            states[opt] = opt_states
        return states

    def save(self):
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
        with open(self.fpath, 'w') as fp:
            json.dump(self.state, fp, indent=4)

    @property
    def state(self):
        return {
            'state': self.name,
            'rules': self.rules.state,
            'round': {
                'next_player': self.next_player_symbol,
                'next_hand': self.next_hand_index,
                'options': self.next_hand_options,
                'next_states': self.next_states,
            },
            'shoe': self.shoe.state,
            'dealer': self.dealer.state,
            'player': self.player.state,
        }


if __name__ == '__main__':
    d = Deal()
    d.save()
