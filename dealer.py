from hand import Hand


class Dealer:
    def __init__(self, table):
        self.table = table
        self.hand = Hand()

    def __repr__(self):
        return f'D {self.hand}'

    @property
    def state(self):
        return {
        }


if __name__ == '__main__':
    from table import Table
    t = Table()
    d = Dealer(t)
    print(d)
