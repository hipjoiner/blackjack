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
    def next_states(self):
        return None

    def save(self):
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
        with open(self.fpath, 'w') as fp:
            json.dump(self.state, fp, indent=4)

    @property
    def state(self):
        return {
            'name': self.name,
            'fpath': self.fpath,
            'table': self.rules.state,
            'round': {
                'next_to_play': self.next_to_play,
                'winner': self.winner,
                'next_states': self.next_states,
            },
            'shoe': self.shoe.state,
            'dealer': self.dealer.state,
            'player': self.player.state,
        }

    @property
    def next_to_play(self):
        # Initial deal
        for num_cards in [0, 1]:
            for p in [self.player, self.dealer]:
                if p.hand.num_cards == num_cards:
                    return p
        return None

    @property
    def winner(self):
        return None


if __name__ == '__main__':
    d = Deal()
    d.save()
