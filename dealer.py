from hand import Hand


class Dealer:
    def __init__(self, table):
        self.table = table
        self.hand = Hand()

    def __repr__(self):
        return self.name

    @property
    def name(self):
        return f'D {self.hand}'

    @property
    def state(self):
        return {
            'name': self.name,
            'hand': self.hand.state,
        }


if __name__ == '__main__':
    from table import Table
    t = Table()
    d = Dealer(t)
    print(d)
