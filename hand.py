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

    Possible hand actions:
        deal (card) (excludes other options)
        blackjack (no card) (excludes other options) (end state)
        surrender (no card) (end state)
        split (card)
        double (card) (end state)
        hit (card)
        stand (no card) (end state)
"""

class Hand:
    symbols = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
    indexes = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'A': 9}

    def __init__(self, player, counts=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], cards=''):
        self.player = player
        self.counts = counts
        for c in cards:
            self.add(c)

    def __str__(self):
        return self.name

    def add(self, card):
        self.counts[self.indexes[card]] += 1

    @property
    def cards(self):
        return dict(zip(self.symbols, self.counts))

    @property
    def hard_total(self):
        return sum([self.counts[i] * self.values[i] for i in self.indexes.values()])

    @property
    def is_blackjack(self):
        return self.total == 21 and self.num_cards == 2

    @property
    def is_busted(self):
        return self.total > 21

    @property
    def is_done(self):
        # Has hand reached a terminal state
        return False

    @property
    def is_pair(self):
        return self.num_cards == 2 and max(self.counts) == 2

    @property
    def is_soft(self):
        return self.total != self.hard_total

    @property
    def name(self):
        return '-'.join([str(c) for c in self.counts])

    @property
    def num_cards(self):
        return sum(self.counts)

    @property
    def state(self):
        return {
            'cards': self.cards,
            'total': self.total,
            'is_blackjack': self.is_blackjack,
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
