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
        self.is_doubled = False
        self.stand = False

    def __str__(self):
        s = self.cards
        if self.player == self.dealer:
            return f'{self.up_card}/{s}({self.total})'
        return f'{s}({self.total})'

    @property
    def bettor(self):
        return self.player.bettor

    @property
    def blackjack(self):
        return self.total == 21 and self.num_cards == 2 and self.splits == 0

    @property
    def can_surrender(self):
        """First two cards only, surrender allowed"""
        return self.first_two and self.rules.surrender

    @property
    def can_split(self):
        """On a pair, if not at maximum splits allowed"""
        if not self.paired:
            return False
        if self.up_card == 'A':
            return self.splits < self.rules.split_aces
        else:
            return self.splits < self.rules.split_2_to_10

    @property
    def can_double(self):
        """Two cards, plus rules"""
        return True

    @property
    def can_hit(self):
        """Can't hit split aces if rules limit; etc."""
        return True

    @property
    def dealer(self):
        return self.player.dealer

    @property
    def final(self):
        # A hand result that makes it possible to determine amount won/lost (from bettor point of view)
        if not self.terminal:
            raise ValueError(f'Attempt to get result of unfinished hand: {self}')
        if self.blackjack:
            if self.dealer.hand.blackjack:
                return 'push'
            return 'blackjack'
        if self.total > 21:
            return 'bust'
        if self.dealer.hand.total > 21:
            return 'dealer bust'
        if self.total > self.dealer.hand.total:
            return 'win'
        if self.total < self.dealer.hand.total:
            return 'lose'
        return 'push'

    @property
    def first_two(self):
        return self.num_cards == 2 and self.splits == 0

    @property
    def min_total(self):
        tot = 0
        for c in self.cards:
            tot += card_value[c]
        return tot

    @property
    def net(self):
        # Betting result of the hand
        mult = {
            'blackjack': self.rules.blackjack_pays,
            'bust': -1.0,
            'dealer bust': 1.0,
            'lose': -1.0,
            'push': 0.0,
            'win': 1.0,
        }
        return self.bet * mult[self.final]

    @property
    def num_cards(self):
        return len(self.cards)

    @property
    def paired(self):
        return self.num_cards == 2 and self.cards[0] == self.cards[1]

    @property
    def rules(self):
        return self.player.table.rules

    @property
    def shoe(self):
        return self.player.table.shoe

    @property
    def soft(self):
        return self.min_total < self.total

    @property
    def splits(self):
        return len(self.player.hands) - 1

    @property
    def terminal(self):
        if self.total >= 21:
            return True
        if self.stand:
            return True
        if self.is_doubled:
            return True
        return False

    @property
    def total(self):
        tot = self.min_total
        if tot <= 11 and 'A' in self.cards:
            tot += 10
        return tot

    def double(self):
        # FIXME: this check needs to be more thorough
        if self.num_cards != 2:
            raise ValueError(f"Can't double hand with {self.num_cards} cards ({self.cards})")
        self.bet *= 2.0
        self.draw()
        self.is_doubled = True

    def draw(self):
        new_card = self.shoe.draw()
        if self.num_cards == 0:
            self.up_card = new_card
        elif self.num_cards == 1:
            self.hole_card = new_card
        self.cards = ''.join(sorted(f'{self.cards}{new_card}'))

    def split(self):
        pass
