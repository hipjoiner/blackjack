import json
import os

from config import home_dir
from table import Table
from shoe import Shoe
from dealer import Dealer
from player import Player


class Deal:
    def __init__(self, table=None, dealer=None, player=None):
        self.table = table
        if self.table is None:
            self.table = Table()
        self.dealer = dealer
        if self.dealer is None:
            self.dealer = Dealer(self.table)
        self.player = player
        if self.player is None:
            self.player = Player(self.table)
        self.shoe = Shoe(self.table.decks)

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
        return f'{self.table} # {self.dealer} # {self.player}'

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
            'table': self.table.data,
            'round': {
                'to_play': self.to_play,
                'winner': self.winner,
                'next_states': self.next_states,
            },
            'shoe': self.shoe.state,
            'dealer': self.dealer.state,
            'player': self.player.state,
        }

    @property
    def to_play(self):
        if self.player.active_hand.num_cards == 0:
            return 'Player'
        if self.dealer.hand.num_cards == 0:
            return 'Dealer'
        if self.player.active_hand.num_cards == 1:
            return 'Player'
        if self.dealer.hand.num_cards == 1:
            return 'Dealer'
        return None

    @property
    def winner(self):
        return None


if __name__ == '__main__':
    d = Deal()
    d.save()
