"""A Hand's cards are orderless. Properties:
        count of cards of each rank
        num_cards
        hard_total
        soft_total
        total
        is_blackjack
        is_busted
        is_doubled
        is_pair
        is_soft
        is_terminal
"""
from config import CachedInstance


class Hand(metaclass=CachedInstance):
    symbols = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
    indexes = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'A': 9}

    def __init__(self, player, counts=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0), cards='', surrendered=False, doubled=False, stand=False):
        self.player = player
        self.counts = list(counts)
        for c in cards:
            self.add(c)
        self.surrendered = surrendered
        self.doubled = doubled
        self.stand = stand
        self.index = 0

    def __str__(self):
        return self.name

    def add(self, card):
        self.counts[self.indexes[card]] += 1

    @property
    def can_deal(self):
        return self.num_cards < 2

    @property
    def can_surrender(self):
        return True

    @property
    def can_split(self):
        return True

    @property
    def can_double(self):
        return True

    @property
    def can_hit(self):
        return True

    @property
    def can_stand(self):
        return True

    @property
    def cards(self):
        return dict(zip(self.symbols, self.counts))

    @property
    def hard_total(self):
        return sum([self.counts[i] * self.values[i] for i in self.indexes.values()])

    @property
    def is_blackjack(self):
        return self.total == 21 and self.num_cards == 2 and self.player.splits == 0

    @property
    def is_busted(self):
        return self.total > 21

    @property
    def is_maxed(self):
        return self.total >= 21

    @property
    def is_pair(self):
        return self.num_cards == 2 and max(self.counts) == 2

    @property
    def is_soft(self):
        return self.total != self.hard_total

    @property
    def is_terminal(self):
        return self.options is None

    @property
    def name(self):
        s = '-'.join([str(c) for c in self.counts])
        if self.surrendered:
            s += '^R'
        elif self.doubled:
            s += '^D'
        if self.stand:
            s += '^S'
        return s

    def new_state(self, card='', surrender=None, double=None, stand=None):
        if surrender is None:
            surrender = self.surrendered
        if double is None:
            double = self.doubled
        if stand is None:
            stand = self.stand
        new_hand = Hand(self.player, tuple(self.counts), cards=card, surrendered=surrender, doubled=double, stand=stand)
        return new_hand

    @property
    def num_cards(self):
        return sum(self.counts)

    @property
    def options(self):
        if self.is_maxed or self.surrendered or self.doubled or self.stand:
            return None
        if self.can_deal:
            return ['Deal']
        opts = []
        if self.can_surrender:
            opts.append('Surrender')
        if self.can_split:
            opts.append('Split')
        if self.can_double:
            opts.append('Double')
        if self.can_hit:
            opts.append('Hit')
        if self.can_stand:
            opts.append('Stand')
        if not opts:
            return None
        return opts

    @property
    def state(self):
        return {
            'cards': self.cards,
            'total': self.total,
            'is_blackjack': self.is_blackjack,
            'surrendered': self.surrendered,
            'doubled': self.doubled,
            'stand': self.stand,
            'is_soft': self.is_soft,
            'is_busted': self.is_busted,
        }

    @property
    def total(self):
        if self.hard_total <= 11 and self.counts[self.indexes['A']] > 0:
            return self.hard_total + 10
        return self.hard_total


if __name__ == '__main__':
    from player import Player
    from rules import Rules
    p = Player(Rules(), is_dealer=False)
    h = Hand(p, cards='AT')
    print(f'Hand:\n{h}')
    print(f'Hand data:\n{h.state}')
