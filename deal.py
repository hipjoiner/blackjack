import os


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
    def cards(self):
        """Full sequence of cards dealt during this deal, in order."""
        d = self.dealer.cards
        b = self.bettor.cards
        hole_card = ''
        if self.dealer.num_cards >= 2:
            hole_card = 'x'
            if self.dealer.hand.revealed:
                hole_card = d[1:2]
        s = b[:1] + d[:1] + b[1:2] + hole_card + b[2:] + d[2:]
        return s

    @property
    def num_cards(self):
        return len(self.cards)

    @property
    def dealer(self):
        return self.table.dealer

    @property
    def dealt(self):
        return self.dealer.hand and self.dealer.hand.num_cards >= 2

    @property
    def done(self):
        return self.dealer.done

    @property
    def fname(self):
        return f'Cards-{self.num_cards};Dealer-{self.dealer};Bettor-{self.bettor}.txt'

    def run(self):
        """Run 1 step of a deal."""
        if self.dealer.num_hands == 0:
            self.bettor.add_hand()
            self.dealer.add_hand()
            self.dealer.hand.revealed = False
        elif self.bettor.num_hands == 1 and self.bettor.hand.num_cards == 0:
            self.bettor.draw()
        elif self.dealer.hand.num_cards == 0:
            self.dealer.draw()
        elif self.bettor.num_hands == 1 and self.bettor.hand.num_cards == 1:
            self.bettor.draw()
        elif self.dealer.hand.num_cards == 1:
            self.dealer.draw()
        elif not self.bettor.done:
            play = self.bettor.play()
            print(f'bettor {play}...')
        elif not self.dealer.done:
            play = self.dealer.play()
            print(f'dealer {play}...')

    def save(self):
        os.makedirs(self.cache, exist_ok=True)
        fpath = f'{self.cache}/{self.fname}'
        if os.path.exists(fpath):
            return
        with open(fpath, 'w') as fp:
            """Data to save:
                Cards total
                Dealer cards
                Player cards
                All possible next play actions
                    Future state resulting from play action
                    If action involves taking a card, all future states with probability of each
            """
            fp.write('some data')
