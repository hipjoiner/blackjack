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
    def __init__(self, player, cards=''):
        self.player = player
        self.up_card = ''               # First card dealt
        self.hole_card = ''             # Second card dealt
        self.cards = cards
        if self.cards:
            self.up_card = self.cards[0]
        if len(self.cards) > 1:
            self.hole_card = self.cards[1]
        self.bet = 1.0
        self.doubled = False
        self.stood = False

    def __str__(self):
        if self.player == self.dealer:
            return f'{self.up_card}/{self.extra_cards}({self.total})'
        s = f'{self.cards}({self.total})'
        if self.outcome != 'Unfinished':
            s += f'{self.outcome}{self.net:+.1f}'
        return s

    @property
    def bettor(self):
        return self.player.bettor

    @property
    def blackjack(self):
        return self.total == 21 and self.num_cards == 2 and self.splits == 0

    @property
    def busted(self):
        return self.total > 21

    @property
    def can_double(self):
        """Two cards, plus rules"""
        return True

    @property
    def can_hit(self):
        """FIXME: Can't hit split aces if rules limit; etc."""
        return True

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
    def can_surrender(self):
        """Only on first two cards, with surrender allowed"""
        return self.first_two and self.rules.surrender

    @property
    def dealer(self):
        return self.player.dealer

    @property
    def extra_cards(self):
        """For showing dealer hand: extras are all cards after up card"""
        up_pos = self.cards.find(self.up_card)
        return self.cards[0:up_pos] + self.cards[up_pos + 1:]


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
            'Blackjack': self.rules.blackjack_pays,
            'Bust': -1.0,
            'DealerBust': 1.0,
            'Lose': -1.0,
            'Push': 0.0,
            'Unfinished': 0.0,
            'Win': 1.0,
        }
        return self.bet * mult[self.outcome]

    @property
    def num_cards(self):
        return len(self.cards)

    @property
    def outcome(self):
        # A hand result that makes it possible to determine amount won/lost (from bettor point of view)
        if not self.dealer.terminal:
            return 'Unfinished'
        if self.blackjack:
            if self.dealer.hand.blackjack:
                return 'Push'
            return 'Blackjack'
        if self.total > 21:
            return 'Bust'
        if self.dealer.hand.total > 21:
            return 'DealerBust'
        if self.total > self.dealer.hand.total:
            return 'Win'
        if self.total < self.dealer.hand.total:
            return 'Lose'
        return 'Push'

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
        if self.busted:
            return True
        if self.doubled:
            return True
        if self.stood:
            return True
        return False

    @property
    def total(self):
        """Best hand total <= 21"""
        tot = self.min_total
        if tot <= 11 and 'A' in self.cards:
            tot += 10
        return tot

    def double(self):
        """Double down"""
        self.bet *= 2.0
        self.draw()
        self.doubled = True

    def draw(self):
        """Add a card from the shoe"""
        new_card = self.shoe.draw()
        if self.num_cards == 0:
            self.up_card = new_card
        elif self.num_cards == 1:
            self.hole_card = new_card
        self.cards = ''.join(sorted(f'{self.cards}{new_card}'))

    def split(self):
        """Split this hand.  Add the new hand to the players hands list."""
        split_card = self.cards[1]
        self.cards = self.cards[0]
        self.hole_card = ''
        new_hand = Hand(self.player, split_card)
        self.player.add_hand(new_hand)
