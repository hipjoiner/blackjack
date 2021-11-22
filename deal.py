import json
import os
from pprint import pprint

from config import data
from table import Table


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

    def deal_card(self):
        player = self.next_player
        if player is None:
            raise ValueError('Tried to deal card but no player wants a card')
        player.add_card(self.table.shoe.get_card())

    @property
    def fpath(self):
        os.makedirs(f'{data}/deals/{self.table.name}', exist_ok=True)
        return f'{data}/deals/{self.table.name}/{self.name}.json'

    @property
    def name(self):
        return f'{self.table.name}-{self.cards}'

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
    def state(self):
        return {
            'name': self.name,
            'table': self.table.state,
            'shoe': self.table.shoe.state,
            'rules': self.table.rules.state,
            'dealer': self.table.dealer.state,
            'bettor': self.table.bettor.state,
        }

    def save(self):
        with open(self.fpath, 'w') as fp:
            json.dump(self.state, fp, indent=4)


if __name__ == '__main__':
    d = Deal('Table1', '878A')
    while len(d.table.shoe.dealt) < len(d.table.shoe.preset):
        d.deal_card()
    print('')
    pprint(d.state)
    d.save()

