from hand import Hand


class Player:
    def __init__(self, table):
        self.table = table
        self.insurance = False
        self.surrendered = False
        self.hands = [Hand()]

    def __repr__(self):
        return self.name

    @property
    def active_hand(self):
        if self.splits == 0:
            return self.hands[0]
        return None

    @property
    def name(self):
        return f'P {" ".join(str(h) for h in self.hands)}'

    @property
    def splits(self):
        return len(self.hands) - 1

    @property
    def state(self):
        return {
            'name': self.name,
            'insurance': self.insurance,
            'surrendered': self.surrendered,
            'splits': self.splits,
            'hands': [h.state for h in self.hands],
        }


if __name__ == '__main__':
    from table import Table
    t = Table()
    p = Player(t)
    print(p)
