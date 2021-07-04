"""
Parameters defining a complete shoe configuration:
    Decks: 1-8
"""
from rules import shoe_decks


class Shoe:
    def __init__(self, decks=8):
        self.decks = decks

    def __str__(self):
        return shoe_decks[self.decks]
