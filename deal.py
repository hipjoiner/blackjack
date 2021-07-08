import os

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
    cache = 'C:/Users/John/blackjack'

    def __init__(self, table):
        self.table = table

    def __str__(self):
        return f'Dealer-{self.dealer};Bettor-{self.bettor}'

    @property
    def bettor(self):
        return self.table.bettor

    @property
    def dealer(self):
        return self.table.dealer

    @property
    def dealt(self):
        return bool(self.dealer.hand)

    @property
    def terminal(self):
        return self.dealer.terminal

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

    def run(self):
        """Run 1 step of a deal."""
        if not self.dealer.hands:
            self.deal_opening_cards()
            if self.check_opening_blackjacks():
                # FIXME: Handle opening blackjack appropriately (end the hand)
                pass
        elif not self.bettor.terminal:
            play = self.bettor.play()
            print(f'bettor {play}...')
        elif not self.dealer.terminal:
            play = self.dealer.play()
            print(f'dealer {play}...')

    def save(self):
        os.makedirs(self.cache, exist_ok=True)
        fpath = f'{self.cache}/{self}.txt'
        if not os.path.exists(fpath):
            with open(fpath, 'w') as fp:
                fp.write('some data')
