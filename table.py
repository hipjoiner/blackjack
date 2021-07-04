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
from rules import Rules, blackjack_payoffs
from shoe import Shoe
from dealer import Dealer
from player import Player


class Table:
    def __init__(self, rules=None, shoe=None, dealer=None, player=None):
        if rules is None:
            rules = Rules()
        self.rules = rules
        if shoe is None:
            shoe = Shoe(decks=self.rules.decks)
        self.shoe = shoe
        if dealer is None:
            dealer = Dealer(self)
        self.dealer = dealer
        if player is None:
            player = Player(self)
        self.player = player

    def __str__(self):
        return f'{blackjack_payoffs[self.rules.blackjack_pays]}|{self.shoe}'
