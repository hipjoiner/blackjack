"""
Parameters defining a complete dealer configuration:
    (All of them come from the rules of the table)
    Dealer peeks for blackjack: true/false
    Dealer hits soft 17: true/false
"""
from player import Player


class Dealer(Player):
    def __str__(self):
        return '|'.join([str(h) for h in self.hands])

    @property
    def hits_soft_17(self):
        return self.table.rules.dealer_hits_soft_17

    @property
    def peeks_for_blackjack(self):
        return self.table.rules.dealer_peeks_for_blackjack

    def choose_play(self, hand):
        """Dealer play is always simple:
            Hit 16 and under, stand on hard 17 and over.
            For soft 17, depends on table rules.
        """
        if hand.total <= 16:
            return 'hits'
        if hand.total == 17 and hand.soft:
            if self.hits_soft_17:
                return 'hits'
            return 'stands'
        return 'stands'
