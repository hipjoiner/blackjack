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
        self.is_doubled = False

    def add_card(self, card):
        play = self.next_play
        if play == 'deal':
            self.cards = f'{self.cards}{card}'
        elif play == 'split':
            self.player.hands.append(Hand(self.player, self.cards[1]))
            self.cards = f'{self.cards[0]}{card}'
        elif play == 'double':
            self.cards = f'{self.cards}{card}'
            self.is_doubled = True
        elif play == 'hit':
            self.cards = f'{self.cards}{card}'
        else:
            raise ValueError(f'Attempt to add card to hand whose next play is {play}')

    @property
    def dealer_up(self):
        cards = self.player.table.dealer.cards
        if len(cards) == 0:
            return None
        return cards[0]

    @property
    def hard_total(self):
        return sum([card_value[c] for c in self.cards])

    @property
    def is_blackjack(self):
        return self.total == 21 and self.num_cards == 2 and len(self.player.hands) == 1

    @property
    def is_busted(self):
        return self.total > 21

    @property
    def is_done(self):
        if self.num_cards < 2:
            return False
        if self.player.opponent.is_final:
            return True
        return self.next_play is None

    @property
    def is_final(self):
        """Final means opponent should not bother taking any cards because outcome is already knowable"""
        return self.is_blackjack or self.is_surrendered or self.is_busted

    @property
    def is_paired(self):
        return self.num_cards == 2 and self.cards[0] == self.cards[1]

    @property
    def is_soft(self):
        return self.total != self.hard_total

    @property
    def is_surrendered(self):
        return self.rules.can_surrender(self) and self.player.strategy.surrender(self, self.dealer_up)

    @property
    def net_value(self):
        if not self.is_done:
            return None
        dh = self.player.table.dealer.hands[0]
        if not dh.is_done:
            return None
        if self.is_blackjack:
            if dh.is_blackjack:
                return 0.0
            return self.rules.blackjack_pays
        if self.is_surrendered:
            return -0.5
        if self.is_busted:
            return -1.0
        if dh.is_blackjack:
            return -1.0
        if dh.is_busted:
            return 1.0
        if self.total > dh.total:
            if self.is_doubled:
                return 2.0
            return 1.0
        if self.total < dh.total:
            if self.is_doubled:
                return -2.0
            return -1.0
        return 0.0

    @property
    def next_play(self):
        if len(self.cards) < 2:
            return 'deal'
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
    def rules(self):
        return self.player.table.rules

    @property
    def splits(self):
        return len(self.player.hands) - 1

    @property
    def state(self):
        if self.player.is_dealer:
            return {
                'cards': self.cards,
                'total': self.total,
                'is_blackjack': self.is_blackjack,
                'is_done': self.is_done,
                'next_play': self.next_play,
            }
        return {
            'cards': self.cards,
            'total': self.total,
            'dealer_up': self.dealer_up,

            'is_done': self.is_done,
            'is_blackjack': self.is_blackjack,
            'is_surrendered': self.is_surrendered,
            'is_soft': self.is_soft,
            'is_split': len(self.player.hands) - 1,
            'is_doubled': self.is_doubled,
            'is_busted': self.is_busted,

            'can_surrender': self.rules.can_surrender(self),
            'can_split': self.rules.can_split(self),
            'can_double': self.rules.can_double(self),
            'can_hit': self.rules.can_hit(self),

            'next_play': self.next_play,
            'net_value': self.net_value,
        }

    @property
    def total(self):
        """Best hand total <= 21"""
        if self.hard_total <= 11 and 'A' in self.cards:
            return self.hard_total + 10
        return self.hard_total


if __name__ == '__main__':
    from table import Table
    t = Table('Table1')
    from player import Player
    b = Player(t, 'Bettor', 'Basic')
    h = Hand(b)
    print('Hand state:')
    print(h.state)
