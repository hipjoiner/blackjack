"""
A hand should have all knowledge necessary to determine what options are available to it next:
    It should know if it's been split and how many times
    It should know if it's been doubled
    It should be able to know the dealer's up card so it can determine if Surrender is legal
        (Dealer's hand/up card should be an integral part of the hand)
    It won't know directly what options it has: it must ask the Rules to determine that.
"""


class Hand:
    def __init__(self, player):
        self.player = player
        self.cards = ''
        self.hard_total = 0
        self.soft_total = 0

    def __str__(self):
        if len(self.cards) == 0:
            return '<none>'
        return self.cards

    def draw(self):
        card = self.shoe.draw()
        self.cards += card
        # Update soft & hard totals, etc.

    @property
    def shoe(self):
        return self.player.table.shoe

    @property
    def terminal(self):
        return False

    @property
    def total(self):
        return self.hard_total
