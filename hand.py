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
        self.bet = 1.0
        self.peeked = False                             # Dealer peeked at hole card for blackjack?
        self.revealed = self.player == self.bettor      # Hole card visible; if dealer, initially False
        self.doubled = False
        self.surrendered = False
        self.stood = False
        self._done = False

    def __str__(self):
        return self.state

    @property
    def bettor(self):
        return self.player.bettor

    @property
    def can_double(self):
        """Two cards, plus rules"""
        if self.rules.double_allowed == 3:      # No double allowed
            return False
        if self.num_cards != 2:
            return False
        if self.splits > 0 and not self.rules.double_after_split:
            return False
        if self.splits > 0 and self.up_card == 'A' and self.rules.split_aces_draw == 1:
            return False
        if self.rules.double_allowed == 0:      # Double any 2
            return True
        if self.rules.double_allowed == 1 and self.total in [9, 10, 11]:
            return True
        if self.rules.double_allowed == 2 and self.total in [10, 11]:
            return True
        return False

    @property
    def can_draw(self):
        return self.num_cards < 2

    @property
    def can_hit(self):
        """Can't hit split aces if rules limit; etc."""
        if self.doubled:
            return False
        if self.splits > 0 and self.up_card == 'A' and self.rules.split_aces_draw == 1:
            return False
        return True

    @property
    def can_peek(self):
        """Can this (dealer's) hand peek now for blackjack?"""
        if not self.rules.dealer_peeks_for_blackjack:
            return False
        if not self.dealer_hand:
            return False
        if self.num_cards != 2 or self.bettor.num_hands != 1 or self.bettor.hand.num_cards != 2:
            return False
        if self.up_card not in ['A', 'T']:
            return False
        if self.revealed:
            return False
        return True

    @property
    def can_reveal(self):
        if not self.dealer_hand:
            return False
        if not self.player.done:
            return False
        if self.revealed:
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
    def can_stand(self):
        if self.num_cards < 2:
            return False
        if self.total > 20:
            return False
        return True

    @property
    def can_surrender(self):
        """Only on first two cards, with surrender allowed"""
        return self.first_two and self.rules.surrender

    @property
    def dealer(self):
        return self.player.dealer

    @property
    def dealer_hand(self):
        return self.player == self.dealer

    @property
    def done(self):
        """Has player finished playing the hand, either by choice or by rule requirements?"""
        if self._done:
            return True
        if self.rules.dealer_peeks_for_blackjack and self.dealer.hand.is_blackjack:
            self._done = True
        if self.is_blackjack:
            self._done = True
        if self.is_busted:
            self._done = True
        if self.doubled:
            self._done = True
        if self.stood:
            self._done = True
        if self.surrendered:
            self._done = True
        return self._done

    @done.setter
    def done(self, value):
        self._done = value

    @property
    def first_two(self):
        return self.num_cards == 2 and self.splits == 0

    @property
    def hole_card(self):
        if self.num_cards < 2:
            return ''
        return self.cards[1]

    @property
    def is_bettor_hand(self):
        return self.player == self.bettor

    @property
    def is_blackjack(self):
        return self.total == 21 and self.num_cards == 2 and self.splits == 0

    @property
    def is_busted(self):
        return self.total > 21

    @property
    def min_total(self):
        return sum([card_value[c] for c in self.cards])

    @property
    def net(self):
        """Betting result of the hand; always from player point of view"""
        if self.result == 'Won':
            if self.is_blackjack:
                return self.bet * self.rules.blackjack_pays
            return self.bet
        if self.result == 'Lost':
            return -self.bet
        return 0.0

    @property
    def num_cards(self):
        return len(self.cards)

    @property
    def paired(self):
        return self.num_cards == 2 and self.cards[0] == self.cards[1]

    @property
    def result(self):
        """Won, lost, or push?  Always from the bettor's point of view.
        (Can't make sense from dealer's point of view, because dealer may face multiple bettor hands.)
        """
        if not self.dealer.done:
            raise ValueError('Attempt to check result before hand has finished play.')
        if self.is_blackjack:
            if self.dealer.hand.is_blackjack:
                return 'Push'
            return 'Won'
        if self.dealer.hand.is_blackjack:
            return 'Lost'
        if self.surrendered:
            return 'Lost'
        if self.total > 21:
            return 'Lost'
        if self.dealer.total > 21:
            return 'Won'
        if self.total > self.dealer.total:
            return 'Won'
        if self.total < self.dealer.total:
            return 'Lost'
        return 'Push'

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
    def state(self):
        s = self.cards
        if self.player.is_dealer:
            if self.num_cards > 1 and not self.revealed:
                s = f'{s[:1]}x'
            if self.peeked:
                s = f'{s}K'
        if self.stood:
            s = f'{s}S'
        if self.doubled:
            s = f'{s}D'
        return s

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
        self.player.cards += new_card
        return new_card

    def next_state(self, action=None, card=''):
        """Hypothetical next state"""
        if action == 'Surrender':
            return f'{self.state}R'
        if action == 'Split':
            return f'{self.cards[0]}{card}_{self.cards[1]}'
        s = f'{self.cards}{card}'
        if self.player.is_dealer:
            # Special dealer actions are Peek, Reveal
            if len(s) > 1 and not self.revealed and action != 'Reveal':
                s = f'{s[:1]}x'
            if self.peeked or action == 'Peek':
                s = f'{s}K'
        if self.stood or action == 'Stand':
            s = f'{s}S'
        if self.doubled or action == 'Double':
            s = f'{s}D'
        return s

    def next_states(self, action):
        """All possible next states based on pdf and action"""
        card_pdf = self.shoe.card_pdf()
        states_pdf = {}
        for card, prob in card_pdf.items():
            new_state = self.next_state(action, card)
            states_pdf[new_state] = card_pdf[card]
        return states_pdf

    def options(self):
        """All play options available currently for this hand.
            C   Draw [1 card]
            K   Peek [for blackjack]
            T   Reveal [hole card]
            R   Surrender
            P   Split
            D   Double
            H   Hit
            S   Stand
        """
        if self.can_draw:
            # If Draw is an option, it is the only option-- you're getting a card
            return ['Draw']
        if self.can_peek:
            # Likewise Peek
            return ['Peek']
        result = []
        if self.can_reveal:
            result.append('Reveal')
        if self.can_surrender:
            result.append('Surrender')
        if self.can_split:
            result.append('Split')
        if self.can_double:
            result.append('Double')
        if self.can_hit:
            result.append('Hit')
        if self.can_stand:
            result.append('Stand')
        return result

    def peek(self):
        self.peeked = True

    def reveal(self):
        self.revealed = True

    def split(self):
        """Split this hand.  Add the new hand to the player's hands list."""
        split_card = self.cards[1]
        self.cards = self.cards[0]
        new_hand = Hand(self.player, split_card)
        self.player.add_hand(new_hand)

    def stand(self):
        self.stood = True

    def surrender(self):
        self.surrendered = True
