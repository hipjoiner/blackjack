from hand import Hand


class Player:
    valid_plays = [
        'Double',
        'Draw',
        'Hit',
        'Reveal',
        'Split',
        'Stand',
        'Surrender',
    ]

    def __init__(self, table):
        self.table = table
        self.hands = []
        self.cards = ''         # Raw card deal sequence, irrespective of splits
        self._done = False

    @property
    def bettor(self):
        return self.table.bettor

    @property
    def dealer(self):
        return self.table.dealer

    @property
    def done(self):
        raise NotImplementedError()

    @done.setter
    def done(self, value):
        raise NotImplementedError()

    @property
    def hand(self):
        if len(self.hands) == 0:
            return None
        return self.hands[0]

    @property
    def live(self):
        """Is the eventual result of all my hands already determined, irrespective of opponent actions?
        This will be so if I have all final hands (blackjacks or busted)
        """
        if self.num_hands == 0:
            return True
        for h in self.hands:
            # Blackjack, surrendered, or busted?
            if not (h.blackjack or h.surrendered or h.busted):
                return True
        return False

    @property
    def num_cards(self):
        if self.num_hands == 0:
            return 0
        return sum([h.num_cards for h in self.hands])

    @property
    def num_hands(self):
        return len(self.hands)

    def add_hand(self, hand=None):
        if hand is None:
            hand = Hand(self)
        self.hands.append(hand)

    def choose_play(self, hand):
        raise NotImplementedError()

    def clear(self):
        self.hands = []
        self.cards = ''
        self.done = False

    def play(self):
        p = None
        for hand in self.hands:
            if hand.done:
                continue
            p = self.choose_play(hand)
            if p == 'Draw':
                hand.draw()       # For split hands, which start a card short
            elif p == 'Reveal':                 # Dealer reveals his hole card
                hand.revealed = True
            elif p == 'Surrender':
                hand.surrender()
            elif p == 'Split':
                hand.split()
            elif p == 'Double':
                hand.double()
            elif p == 'Hit':
                hand.draw()
            elif p == 'Stand':
                hand._done = True
            else:
                raise ValueError(f'Bad play choice: {p}')
            return p
