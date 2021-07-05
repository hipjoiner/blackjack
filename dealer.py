"""
Parameters defining a complete dealer configuration:
    (All of them come from the rules of the table)
    Dealer peeks for blackjack: true/false
    Dealer hits soft 17: true/false
"""
from player import Player


class Dealer(Player):
    @property
    def hits_soft_17(self):
        return self.table.rules.dealer_hits_soft_17

    @property
    def peeks_for_blackjack(self):
        return self.table.rules.dealer_peeks_for_blackjack

    def choose_play(self, hand):
        if hand.total < 17:
            play = 'Hit'
        elif hand.total == 17 and hand.soft:
            play = 'Hit'
        else:
            play = 'Stand'
        return play
