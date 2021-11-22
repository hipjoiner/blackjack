import json

from config import cache
from rules import Rules
from shoe import Shoe
from player import Player


class Table:
    def __init__(self, name, preset=''):
        self.name = name
        self.spec = None
        with open(self.fpath, 'r') as fp:
            self.spec = json.load(fp)
        self.rules = Rules(self.spec['rules'])
        self.shoe = Shoe(self.decks, preset=preset)
        self.dealer = Player(self, 'Dealer', self.spec['dealer'])
        self.bettor = Player(self, 'Bettor', self.spec['bettor'])

    @property
    def decks(self):
        return self.spec['decks']

    @property
    def fpath(self):
        return f'{cache}/tables/{self.name}.json'

    @property
    def state(self):
        return self.spec
