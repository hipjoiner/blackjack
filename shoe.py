from hand import Hand


class Shoe(Hand):
    def __init__(self, decks):
        super().__init__()
        self.decks = decks
        self.counts = [self.decks * 4] * 8 + [self.decks * 4 * 4] + [self.decks * 4]

    def __repr__(self):
        return f'{self.decks}D'

    @property
    def data(self):
        return {
            'cards': self.cards,
            'pdf': self.pdf,
        }


if __name__ == '__main__':
    pass
