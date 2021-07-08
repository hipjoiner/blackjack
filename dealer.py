"""
Parameters defining a complete dealer configuration:
    (All of them come from the rules of the table)
    Dealer peeks for blackjack: true/false
    Dealer hits soft 17: true/false
"""
from player import Player


class Dealer(Player):
    def __str__(self):
        return str(self.hand)

    @property
    def hits_soft_17(self):
        return self.table.rules.dealer_hits_soft_17

    @property
    def peeks_for_blackjack(self):
        return self.table.rules.dealer_peeks_for_blackjack

    @property
    def up_card(self):
        return self.hand.up_card

    def choose_play(self, hand):
        """Dealer play is always simple: hit <17; stand >17; soft 17 depends on table rules."""
        if hand.total < 17:
            return 'hits'
        if hand.total > 17:
            return 'stands'
        if hand.soft and self.hits_soft_17:
            return 'hits'
        return 'stands'
