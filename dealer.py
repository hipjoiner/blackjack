"""
Parameters defining a complete dealer configuration:
    (All of them come from the rules of the table)
    Dealer peeks for blackjack: true/false
    Dealer hits soft 17: true/false
"""
from rules import dealer_peek_options, dealer_hit_options


class Dealer:
    def __init__(self, table):
        self.table = table

    @property
    def peeks_for_blackjack(self):
        return self.table.rules.dealer_peeks_for_blackjack

    @property
    def hits_soft_17(self):
        return self.table.rules.dealer_hits_soft_17

    def __str__(self):
        return f'{dealer_peek_options[self.peeks_for_blackjack]}|{dealer_hit_options[self.hits_soft_17]}'
