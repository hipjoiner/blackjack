"""
"""
import json

from config import cache
from rules import Rules
from shoe import Shoe
from dealer import Dealer
from bettor import Bettor
from deal import Deal


class Table:
    def __init__(self, name):
        self.name = name
        with open(self.fpath, 'r') as fp:
            self.spec = json.load(fp)

        self.rules = Rules(self.spec['rules'])
        self.shoe = Shoe(self.decks)
        self.dealer = Dealer(self, self.spec['dealer'])
        self.bettor = Bettor(self, self.spec['bettor'])
        self.deal = Deal(self)

    def __str__(self):
        if self.deal is None:
            return 'Empty table'
        return str(self.deal)

    @property
    def decks(self):
        return self.spec['decks']

    @property
    def fpath(self):
        return f'{cache}/tables/{self.name}.json'

    def clear(self):
        self.deal.clear()
        if self.shoe.depleted():
            print('\nShoe depleted; reshuffling...')
            self.shoe.shuffle()

    def deal_hand(self):
        while not self.deal.done:
            if str(self.deal):
                print(f'{self.deal}; ', end='')
            play = self.deal.run()
            if play:
                print(play)
            self.deal.save()
        print(self.deal)
        print('Result: ' + '; '.join([f'{h.result} {h.net}' for h in self.bettor.hands]))
        print(f'Net: {self.bettor.net}')
