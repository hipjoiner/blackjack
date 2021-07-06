from hand import Hand


class Player:
    def __init__(self, table):
        self.table = table
        self.hands = []

    def __str__(self):
        return '|'.join([str(h) for h in self.hands])

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

    def play(self, n=0):
        """Play options:
            Hit
            Stand
            Double
            Split
            Surrender
        """
        p = None
        for hand in self.hands:
            if hand.terminal:
                continue
            p = self.choose_play(hand)
            if p == 'Hit':
                hand.draw()
            elif p == 'Stand':
                hand.stand = True
            elif p == 'Double':
                print('<FIXME: implement doubles>')
            elif p == 'Split':
                print('<FIXME: implement splits>')
            elif p == 'Surrender':
                print('<FIXME: implement surrenders>')
            else:
                raise ValueError(f'Bad play choice: {p}')
        return p
