"""
A hand should have all knowledge necessary to determine what options are available to it next:
    It should know if it's been split and how many times
    It should know if it's been doubled
    It should be able to know the dealer's up card so it can determine if Surrender is legal
        (Dealer's hand/up card should be an integral part of the hand)
    It won't know directly what options it has: it must ask the Rules to determine that.
"""

card_value = {
    'A': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'T': 10,
}


class Hand:
    def __init__(self, player):
        self.player = player
        self.cards = ''
        self.up_card = ''           # First card dealt; only relevant for dealer
        self.hole_card = ''         # Second card dealt; only relevant for dealer
        self.extra_cards = ''       # For dealer, all cards after up & hole cards
        self.bet = 1.0
        self.stand = False

    def __str__(self):
        s = self.cards
        return f'{s}({self.total})'

    def draw(self):
        new_card = self.shoe.draw()
        self.cards = f'{self.cards}{new_card}'
        if self.num_cards == 1:
            self.up_card = new_card
        elif self.num_cards == 2:
            self.hole_card = new_card
        self.cards = ''.join(sorted(self.cards))

    @property
    def min_total(self):
        tot = 0
        for c in self.cards:
            tot += card_value[c]
        return tot

    @property
    def num_cards(self):
        return len(self.cards)

    @property
    def shoe(self):
        return self.player.table.shoe

    @property
    def soft(self):
        return self.min_total < self.total

    @property
    def terminal(self):
        if self.total >= 21:
            return True
        if self.stand:
            return True
        return False

    @property
    def total(self):
        tot = self.min_total
        if tot <= 11 and 'A' in self.cards:
            tot += 10
        return tot
