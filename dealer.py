"""
Parameters defining a complete dealer configuration:
    (All of them come from the rules of the table)
    Dealer peeks for blackjack: true/false
    Dealer hits soft 17: true/false
"""
from player import Player


class Dealer(Player):
    def __str__(self):
        if self.hand is None:
            return ''
        return str(self.hand)

    @property
    def blackjack(self):
        return self.hand.blackjack

    @property
    def busted(self):
        return self.hand.busted

    @property
    def done(self):
        if self._done:
            return True
        if self.hand and not self.hand.revealed:
            return False
        if not self.bettor.live:
            self._done = True
        if self.hand and self.hand.done:
            self._done = True
        return self._done

    @done.setter
    def done(self, value):
        self._done = value

    @property
    def hits_soft_17(self):
        return self.table.rules.dealer_hits_soft_17

    @property
    def peeks_for_blackjack(self):
        return self.table.rules.dealer_peeks_for_blackjack

    @property
    def total(self):
        return self.hand.total

    @property
    def up_card(self):
        return self.hand.up_card

    def choose_play(self, hand):
        """Dealer play is always simple: hit <17; stand >17; soft 17 depends on table rules."""
        if not hand.revealed:
            return 'Reveal'
        if hand.total < 17:
            return 'Hit'
        if hand.total > 17:
            return 'Stand'
        if hand.soft and self.hits_soft_17:
            return 'Hit'
        return 'Stand'
