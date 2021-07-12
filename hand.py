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
        self.cards = cards
        self.revealed = True            # Hole card visible; dealer will initially set this False
        self.bet = 1.0
        self.doubled = False
        self._done = False

    def __str__(self):
        if self.player == self.bettor:
            return self.cards
        if not self.dealer.hand or not self.dealer.hand.num_cards:
            return ''
        if self.dealer.hand.num_cards == 1:
            return self.up_card
        if not self.dealer.hand.revealed:
            return f'{self.up_card}x'
        return self.cards

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
        if self.rules.double_allowed == 3:      # No double allowed
            return False
        if self.num_cards != 2:
            return False
        if self.splits > 0 and not self.rules.double_after_split:
            return False
        if self.rules.double_allowed == 0:      # Double any 2
            return True
        if self.rules.double_allowed == 1 and self.total in [9, 10, 11]:
            return True
        if self.rules.double_allowed == 2 and self.total in [10, 11]:
            return True
        return False

    @property
    def can_hit(self):
        """Can't hit split aces if rules limit; etc."""
        if self.doubled:
            return False
        if self.splits > 0 and self.up_card == 'A' and self.rules.split_aces_draw == 1:
            return False
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
    def done(self):
        """Has player finished playing the hand?"""
        if self._done:
            return True
        if not self.revealed:
            return False
        if self.rules.dealer_peeks_for_blackjack and self.dealer.hand.blackjack:
            self._done = True
        if self.blackjack:
            self._done = True
        if self.busted:
            self._done = True
        if self.doubled:
            self._done = True
        return self._done

    @done.setter
    def done(self, value):
        self._done = value

    @property
    def final(self):
        """Is the eventual result of the hand already determined, irrespective of opponent actions?
        This will be so if I have a blackjack or a busted hand.
        """
        return self.blackjack or self.busted

    @property
    def first_two(self):
        return self.num_cards == 2 and self.splits == 0

    @property
    def hole_card(self):
        if self.num_cards < 2:
            return ''
        return self.cards[1]

    @property
    def min_total(self):
        return sum([card_value[c] for c in self.cards])

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
        if not self.dealer.done:
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
    def total(self):
        """Best hand total <= 21"""
        tot = self.min_total
        if tot <= 11 and 'A' in self.cards:
            tot += 10
        return tot

    @property
    def up_card(self):
        if self.num_cards < 1:
            return ''
        return self.cards[0]

    def double(self):
        """Double down"""
        self.bet *= 2.0
        self.draw()
        self.doubled = True

    def draw(self):
        """Add a card from the shoe"""
        new_card = self.shoe.draw()
        self.cards += new_card
        return new_card

    def split(self):
        """Split this hand.  Add the new hand to the players hands list."""
        split_card = self.cards[1]
        self.cards = self.cards[0]
        new_hand = Hand(self.player, split_card)
        self.player.add_hand(new_hand)
