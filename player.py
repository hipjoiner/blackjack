"""
Parameters defining a complete player configuration:
    (All of them come from the rules of the table)
    Doubling options
    Double after split allowed
    Split 2 to 10 options
    Split aces options
    Split aces draw options
    Surrender options
"""
from rules import double_options, split_2_to_10_options, split_aces_options, split_aces_draw_options, \
    double_after_split_options, surrender_options


class Player:
    def __init__(self, table):
        self.table = table

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

    def __str__(self):
        return '|'.join([
            double_options[self.double],
            double_after_split_options[self.double_after_split],
            split_2_to_10_options[self.split_2_to_10],
            split_aces_options[self.split_aces],
            split_aces_draw_options[self.split_aces_draw],
            surrender_options[self.surrender],
        ])
