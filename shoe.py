import numpy as np


class Shoe:
    symbols = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
    indexes = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'A': 9}

    def __init__(self, deal):
        self.deal = deal
        self.decks = deal.rules.shoe_decks
        self.base_counts = [self.decks * 4] * 8 + [self.decks * 4 * 4] + [self.decks * 4]

    def __repr__(self):
        return f'{self.decks}D'

    @property
    def cards(self):
        return dict(zip(self.symbols, self.counts))

    @property
    def cards_out(self):
        outs = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        outs += self.deal.dealer.counts
        for h in self.deal.player:
            outs += h.counts
        return outs

    @property
    def counts(self):
        return self.base_counts - self.cards_out

    @property
    def num_cards(self):
        return sum(self.counts)

    @property
    def pdf(self):
        probs = [self.counts[i] / self.num_cards if self.num_cards != 0 else 0 for i in self.indexes.values()]
        return dict(zip(self.symbols, probs))


if __name__ == '__main__':
    pass
