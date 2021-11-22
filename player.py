from hand import Hand
from strategy import Strategy


class Player:
    def __init__(self, table, strategy_name, is_bettor):
        self.table = table
        self.is_bettor = is_bettor
        self.strategy = Strategy(strategy_name)
        self.hands = [Hand(self)]
        self.cards = ''

    @property
    def is_dealer(self):
        return not self.is_bettor

    @property
    def is_done(self):
        return self.next_hand is None

    @property
    def net_value(self):
        if self.is_dealer:
            return None
        subtot = 0.0
        for hand in self.hands:
            if hand.net_value is None:
                return None
            subtot += hand.net_value
        return subtot

    @property
    def next_hand(self):
        """Return reference to next hand to play, or None if all hands are done"""
        for hand in self.hands:
            if not hand.is_done:
                return hand
        return None

    @property
    def state(self):
        if self.is_dealer:
            return {
                'strategy': self.strategy.name,
                'is_done': self.is_done,
                'hand': self.hands[0].state,
            }
        return {
            'strategy': self.strategy.name,
            'cards': self.cards,
            'is_done': self.is_done,
            'net_value': self.net_value,
            'hands': [hand.state for hand in self.hands],
        }

    def add_card(self, card):
        if self.next_hand is None:
            raise ValueError(f'Tried to deal card to player but no hand wants one')
        self.cards = f'{self.cards}{card}'
        self.next_hand.add_card(card)
