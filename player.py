from hand import Hand
from strategy import Strategy


class Player:
    def __init__(self, table, strategy_name, is_bettor):
        self.table = table
        self.is_bettor = is_bettor
        self.strategy = Strategy(strategy_name)
        self.hand = Hand(self)
        self.cards = ''

    def add_card(self, card):
        self.cards = f'{self.cards}{card}'
        self.hand.add_card(card)

    @property
    def is_dealer(self):
        return not self.is_bettor

    @property
    def is_done(self):
        return self.hand.is_done

    @property
    def is_final(self):
        return self.hand.is_final

    @property
    def net_value(self):
        if self.is_dealer:
            return None
        return self.hand.net_value

    @property
    def opponent(self):
        if self.is_dealer:
            return self.table.bettor
        return self.table.dealer

    @property
    def state(self):
        if self.is_dealer:
            return {
                'strategy': self.strategy.name,
                'is_done': self.is_done,
                'hand': self.hand.state,
            }
        return {
            'strategy': self.strategy.name,
            'cards': self.cards,
            'is_done': self.is_done,
            'net_value': self.net_value,
            'hand': self.hand.state,
        }
