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
        self.splits = 0

    def add_card(self, card):
        play = self.next_play
        if play == 'deal':
            self.cards = f'{self.cards}{card}'
        elif play == 'split':
            """FIXME: The Great Split Approximation.
            Normally splitting creates two hands with a single card of the same rank (the "split rank").
            Each of those hands gets one more card, and then bettor plays them as any other going forward.
            Assume instead that splitting removes the second card, and changes the bet size to the number of splits.
            So on first split of 8s, bettor would remove the second 8, double his bet, and get a new second card.
            I THINK this results in a nearly identical expected value, but increased variance 
            (which I don't care about).  But not sure.
            """
            self.splits += 1
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
        return self.total == 21 and self.num_cards == 2 and self.splits == 0 and not self.is_doubled

    @property
    def is_busted(self):
        return self.total > 21

    @property
    def is_done(self):
        if self.num_cards < 2:
            return False
        if self.is_final:
            return True
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
    def is_split(self):
        return self.splits > 0

    @property
    def is_surrendered(self):
        return self.rules.can_surrender(self) and self.player.strategy.surrender(self, self.dealer_up)

    @property
    def net_value(self):
        if not self.is_done:
            return None
        dh = self.player.table.dealer.hand
        if not dh.is_done:
            return None
        if self.is_blackjack:
            if dh.is_blackjack:
                return 0.0
            return self.rules.blackjack_pays
        if dh.is_blackjack and self.player.table.rules.dealer_peeks_for_blackjack:
            return -1.0
        if self.is_surrendered:
            return -0.5
        mult = (1.0 + self.splits)
        if self.is_doubled:
            mult *= 2.0
        if dh.is_blackjack:
            return -mult
        if self.is_busted:
            return -mult
        if dh.is_busted:
            return mult
        if self.total > dh.total:
            return mult
        if self.total < dh.total:
            return -mult
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
            'is_split': self.splits,
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
