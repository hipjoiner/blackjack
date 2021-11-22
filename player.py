from hand import Hand
from strategy import Strategy


class Player:
    def __init__(self, table, name, strategy_name):
        self.table = table
        self.name = name
        self.strategy = Strategy(strategy_name)
        self.hands = [Hand(self)]
        self.cards = ''

    @property
    def is_done(self):
        return self.next_hand is None

    @property
    def next_hand(self):
        """Return reference to next hand to play, or None if all hands are done"""
        for hand in self.hands:
            if not hand.is_done:
                return hand
        return None

    @property
    def state(self):
        return {
            'name': self.name,
            'strategy': self.strategy.name,
            'cards': self.cards,
            'hands': [hand.state for hand in self.hands],
        }

    def add_card(self, card):
        if self.next_hand is None:
            raise ValueError(f'Tried to deal card to {self.name} but no hand wants one')
        self.cards = f'{self.cards}{card}'
        self.next_hand.add_card(card)
