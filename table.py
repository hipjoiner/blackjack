"""
Parameters defining a complete table configuration:
    Rules
        Table
            Blackjack pays:                 3-2, 7-5, 6-5, 1-1
            Shoe decks:                     1-8
        Dealer
            Dealer peeks for blackjack:     True/False
            Dealer hits soft 17:            True/False
        Player
            Doubling:                       any 2 cards, 9-11, 10-11, not allowed
            Split 2-10s:                    3 times, 2 times, 1 time, not allowed
            Split aces:                     3 times, 2 times, 1 time, not allowed
            Draw to split aces:             1 only, any
            Double after split:             True/False
            Surrender:                      any, any except ace, none
"""
from shoe import Shoe
from dealer import Dealer
from bettor import Bettor


class Table:
    def __init__(self, rules):
        self.rules = rules
        self.shoe = Shoe(rules.decks)
        self.dealer = Dealer(self)
        self.bettor = Bettor(self)

    def __str__(self):
        if not self.dealer.hand:
            return 'No cards'
        return f'Dealer/{self.dealer}|Bettor/{self.bettor}'

    def clear(self):
        self.dealer.clear_hands()
        self.bettor.clear_hands()
        if self.shoe.depleted():
            print('\nShoe depleted; reshuffling...')
            self.shoe.shuffle()
