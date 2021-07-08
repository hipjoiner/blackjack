from hand import Hand


class Player:
    def __init__(self, table):
        self.table = table
        self.hands = []

    @property
    def bettor(self):
        return self.table.bettor

    @property
    def dealer(self):
        return self.table.dealer

    @property
    def hand(self):
        if len(self.hands) == 0:
            return ''
        return self.hands[0]

    @property
    def terminal(self):
        if not self.hands:
            return False
        for hand in self.hands:
            if not hand.terminal:
                return False
        return True

    def add_hand(self, hand=None):
        if hand is None:
            hand = Hand(self)
        self.hands.append(hand)

    def choose_play(self, hand):
        raise NotImplementedError()

    def clear_hands(self):
        self.hands = []

    def play(self):
        p = None
        for hand in self.hands:
            if hand.terminal:
                continue
            p = self.choose_play(hand)
            if p == 'draws':
                hand.draw()             # For split hands, which start a card short
            elif p == 'surrenders':
                print('<FIXME: implement surrenders>')
            elif p == 'splits':
                hand.split()
            elif p == 'doubles':
                hand.double()
            elif p == 'hits':
                hand.draw()
            elif p == 'stands':
                hand.stood = True
            else:
                raise ValueError(f'Bad play choice: {p}')
            return p
