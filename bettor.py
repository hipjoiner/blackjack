"""
Parameters defining a complete bettor configuration:
    (All of them come from the rules of the table)
    Doubling options
    Double after split allowed
    Split 2 to 10 options
    Split aces options
    Split aces draw options
    Surrender options
"""
from player import Player


class Bettor(Player):
    def __str__(self):
        return '|'.join([str(h) for h in self.hands])

    @property
    def double(self):
        return self.table.rules.double_allowed

    @property
    def double_after_split(self):
        return self.table.rules.double_after_split

    @property
    def split_2_to_10(self):
        return self.table.rules.split_2_to_10

    @property
    def split_aces(self):
        return self.table.rules.split_aces

    @property
    def split_aces_draw(self):
        return self.table.rules.split_aces_draw

    @property
    def surrender(self):
        return self.table.rules.surrender

    def choose_play(self, hand):
        """This function governs all player choices about how to play each hand.
        Initially, we'll implement "optimal" non-counting play strategy.
        """
        if hand.can_surrender and self.should_surrender(hand):
            pass
        if hand.can_split and self.should_split(hand):
            pass
        if hand.can_double and self.should_double(hand):
            pass
        if hand.can_hit and self.should_hit(hand):
            pass
        if hand.total < 17:
            return 'hits'
        return 'stands'

    def should_surrender(self, hand):
        return False

    def should_split(self, hand):
        return False

    def should_double(self, hand):
        return False

    def should_hit(self, hand):
        return False
