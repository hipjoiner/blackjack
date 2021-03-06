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
        self.dealer = Player(self, self.spec['dealer'], is_bettor=False)
        self.bettor = Player(self, self.spec['bettor'], is_bettor=True)

    @property
    def decks(self):
        return self.spec['decks']

    @property
    def fpath(self):
        return f'{cache}/tables/{self.name}.json'

    @property
    def state(self):
        return {
            'rules': self.spec['rules'],
            'decks': self.decks,
            'dealer_strategy': self.spec['dealer'],
            'bettor_strategy': self.spec['bettor'],
        }
