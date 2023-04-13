class Shoe:
    symbols = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
    indexes = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'A': 9}

    def __init__(self, decks):
        self.decks = decks
        self.counts = [self.decks * 4] * 8 + [self.decks * 4 * 4] + [self.decks * 4]

    def __repr__(self):
        return f'{self.decks}D'

    @property
    def cards(self):
        return dict(zip(self.symbols, self.counts))

    @property
    def name(self):
        return '-'.join([str(c) for c in self.counts])

    @property
    def num_cards(self):
        return sum(self.counts)

    @property
    def pdf(self):
        probs = [self.counts[i] / self.num_cards if self.num_cards != 0 else 0 for i in self.indexes.values()]
        return dict(zip(self.symbols, probs))

    @property
    def state(self):
        return {
            'cards': self.cards,
            'pdf': self.pdf,
        }


if __name__ == '__main__':
    pass
