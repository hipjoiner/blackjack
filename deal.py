from hand import Hand


class Deal:
    """
    A Deal is a fully dealt round of blackjack, options exhausted, hands final, wins/losses all determined.
    A Deal incorporates both player activity and dealer activity.
    The Deal is the focus for computation of expected value.
    The Deal will start with a single bettor hand, but the bettor may split into two or more hands.
    We compute expected value for each of the splits of course, since we are computing recursively,
        but the deal EV is the one of primary interest to us.
    """
    def __init__(self, table):
        self.table = table

    @property
    def bettor(self):
        return self.table.bettor

    @property
    def dealer(self):
        return self.table.dealer

    @property
    def terminal(self):
        return self.bettor.terminal and self.dealer.terminal

    def check_opening_blackjacks(self):
        """If dealer doesn't peek, then blackjacks are resolved at the end of the hand like everything else.
        If dealer does peek, then the hand can end, either with a dealer blackjack, OR a player blackjack.
        Return True here if dealer peek results in a terminal state; False otherwise.
        """
        if not self.dealer.peeks_for_blackjack:
            return False
        if self.dealer.hand.total == 21 or self.bettor.hand.total == 21:
            return True
        return False

    def deal_opening_cards(self):
        """Deal 2 opening cards to bettor and player.
        Return True if this step is terminal (blackjack for someone); False if not.
        """
        dhand = Hand(self.dealer)
        bhand = Hand(self.bettor)
        dhand.draw()
        bhand.draw()
        dhand.draw()
        bhand.draw()
        self.dealer.add_hand(dhand)
        self.bettor.add_hand(bhand)

    def run(self, max_steps=0):
        """Run n steps of a deal (max_steps 0 means run to termination)."""
        steps = 0
        if not self.dealer.hands:
            # Count opening deal as 1 step
            print('Opening deal...')
            self.deal_opening_cards()
            # Part of opening deal is dealer peeking for blackjack, if appropriate
            steps += 1
            if self.check_opening_blackjacks():
                return
            if 0 < max_steps <= steps:
                return
        while not self.bettor.terminal:
            print('bettor play: ', end='')
            play = self.bettor.play(1)
            print(play)
            steps += 1
            if 0 < max_steps <= steps:
                return
        while not self.dealer.terminal:
            print('dealer play: ', end='')
            play = self.dealer.play(1)
            print(play)
            steps += 1
            if 0 < max_steps <= steps:
                return
