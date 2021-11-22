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

    @property
    def dealer_up(self):
        return self.player.table.dealer.cards[0]

    @property
    def hard_total(self):
        return sum([card_value[c] for c in self.cards])

    @property
    def is_blackjack(self):
        return self.total == 21 and self.num_cards == 2 and len(self.player.hands) == 1

    @property
    def is_done(self):
        # FIXME: Lots more here
        if self.total >= 21:
            return True
        return False

    @property
    def is_paired(self):
        return self.num_cards == 2 and self.cards[0] == self.cards[1]

    @property
    def is_soft(self):
        return self.total != self.hard_total

    @property
    def net(self):
        """Betting result of the hand; always from player point of view"""
        if self.result == 'Won':
            if self.is_blackjack:
                return self.rules.blackjack_pays
            return 1.0
        if self.result == 'Lost':
            return -1.0
        return 0.0

    @property
    def next_play(self):
        if self.rules.can_surrender(self) and self.player.strategy.surrender(self, self.dealer_up):
            return 'surrender'
        if self.rules.can_split(self) and self.player.strategy.split(self, self.dealer_up):
            return 'split'
        if self.rules.can_double(self) and self.player.strategy.double(self, self.dealer_up):
            return 'double'
        if self.rules.can_hit(self) and self.player.strategy.hit(self, self.dealer_up):
            return 'hit'
        return None

    @property
    def num_cards(self):
        return len(self.cards)

    @property
    def result(self):
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
    def splits(self):
        return len(self.player.hands) - 1

    @property
    def state(self):
        return {
            'cards': self.cards,
            'total': self.total,
            'can_double': self.rules.can_double(self),
            'can_hit': self.rules.can_hit(self),
            'can_split': self.rules.can_split(self),
            'can_surrender': self.rules.can_surrender(self),
            'is_blackjack': self.is_blackjack,
            'splits': len(self.player.hands) - 1,
            'next_play': self.next_play,
            'dealer_up': self.dealer_up,
        }

    @property
    def total(self):
        """Best hand total <= 21"""
        if self.hard_total <= 11 and 'A' in self.cards:
            return self.hard_total + 10
        return self.hard_total

    def add_card(self, card):
        # FIXME: This is where a split would require special handling
        self.cards = f'{self.cards}{card}'


if __name__ == '__main__':
    from table import Table
    t = Table('Table1')
    from player import Player
    b = Player(t, 'Bettor', 'Basic')
    h = Hand(b)
    print('Hand state:')
    print(h.state)
