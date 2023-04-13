from hand import Hand


class Player:
    def __init__(self, rules, is_dealer):
        self.rules = rules
        self.is_dealer = is_dealer
        self.symbol = 'D' if is_dealer else 'P'
        self.hands = [Hand(self)]

    def __repr__(self):
        return self.name

    @property
    def hand(self):
        return self.hands[0]

    @property
    def is_done(self):
        for h in self.hands:
            if not h.is_done:
                return False
        return True

    @property
    def name(self):
        return f'P {" ".join(str(h) for h in self.hands)}'

    @property
    def next_hand(self):
        return None

    @property
    def splits(self):
        return len(self.hands) - 1

    @property
    def state(self):
        return {
            'name': self.name,
            'splits': self.splits,
            'hands': [h.state for h in self.hands],
        }


if __name__ == '__main__':
    from rules import Rules
    t = Rules()
    p = Player(t, is_dealer=False)
    print(p)
