from hand import Hand
from strategy import Strategy


class Player:
    valid_plays = [
        'Draw',
        'Reveal',
        'Surrender',
        'Split',
        'Double',
        'Hit',
        'Stand',
    ]

    def __init__(self, table, strategy_name):
        self.table = table
        self.strategy = Strategy(strategy_name)
        self.hands = [Hand(self)]
        self.cards = ''         # Raw card deal sequence, irrespective of splits
        self._done = False

    @property
    def bettor(self):
        if not hasattr(self.table, 'bettor'):
            return None
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
    def is_bettor(self):
        return self == self.table.bettor

    @property
    def is_dealer(self):
        return self == self.table.dealer

    @property
    def live(self):
        """Is the eventual result of all my hands already determined, irrespective of opponent actions?
        This will be so if I have all final hands (blackjacks or busted)
        """
        if self.num_hands == 0:
            return True
        for h in self.hands:
            # Blackjack, surrendered, or busted?
            if not (h.is_blackjack or h.surrendered or h.is_busted):
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
        self.hands = [Hand(self)]
        self.cards = ''
        self.done = False

    def hand_to_play(self):
        """Determine player's hand that is next to make a play.
        Here we number the hands starting with 1, 2, etc, so that values of
        0 and None-- boolean False-- all represent no hands being playable.
        """
        for i, hand in enumerate(self.hands):
            if not hand.done:
                return i + 1
        return None

    def play(self):
        for hand in self.hands:
            if hand.done:
                continue
            p = self.choose_play(hand)
            hand_fns = {
                'Double': hand.double,
                'Draw': hand.draw,
                'Hit': hand.draw,
                'Reveal': hand.reveal,
                'Split': hand.split,
                'Stand': hand.stand,
                'Surrender': hand.surrender,
            }
            fn = hand_fns[p]
            fn()
            return p
