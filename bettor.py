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
    def __init__(self, table):
        super().__init__(table)
        self.splits = 0

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
        if hand.total < 17:
            play = 'Hit'
        else:
            play = 'Stand'
        return play
