import json
import os

from config import home_dir
from table import Table
from shoe import Shoe
from dealer import Dealer
from player import Player


class State:
    def __init__(self):
        self.table = Table()
        self.shoe = Shoe(6)
        self.dealer = Dealer(self.table)
        self.player = Player(self.table)

    def __repr__(self):
        return self.name

    @property
    def data(self):
        return {
            'name': self.name,
            'fpath': self.fpath,
            'table': self.table.data,
            'shoe': self.shoe.data,
            'dealer': self.dealer.data,
            'player': self.player.data,
            'to_play': self.to_play,
        }

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

    def save(self):
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
        with open(self.fpath, 'w') as fp:
            json.dump(self.data, fp, indent=4)


if __name__ == '__main__':
    d = State()
    d.save()
