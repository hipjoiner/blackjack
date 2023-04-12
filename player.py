from hand import Hand


class Player:
    def __init__(self, table):
        self.table = table
        self.hands = [Hand()]

    def __repr__(self):
        return f'P {" ".join(str(h) for h in self.hands)}'

    @property
    def state(self):
        return {
        }


if __name__ == '__main__':
    from table import Table
    t = Table()
    p = Player(t)
    print(p)
