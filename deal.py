import json
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
        self.history = []
        self.save()

    def __str__(self):
        return self.state

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
        if not s:
            return 'none'
        return s

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
        """Sequence of cards dealt, in order (with dealer hole card visible)"""
        return f'{self.state}.txt'

    @property
    def next_to_play(self):
        return '<incomplete>'

    @property
    def num_cards(self):
        return len(self.cards)

    @property
    def shoe(self):
        return self.table.shoe

    @property
    def state(self):
        d = str(self.dealer.hand)
        if d == 'None':
            d = ''
        b = [f'{str(h)}' for h in self.bettor.hands]
        if not b:
            b = ['']
        return '-'.join(['Deal'] + [d] + b)

    def clear(self):
        self.dealer.clear()
        self.bettor.clear()

    def run(self):
        """Run 1 step of a deal."""
        self.history.append(self.state)
        if self.bettor.num_hands == 1 and self.bettor.hand.num_cards == 0:
            self.bettor.hand.draw()
            action = 'Deal'
        elif self.dealer.hand.num_cards == 0:
            self.dealer.hand.draw()
            action = 'Deal'
        elif self.bettor.num_hands == 1 and self.bettor.hand.num_cards == 1:
            self.bettor.hand.draw()
            action = 'Deal'
        elif self.dealer.hand.num_cards == 1:
            self.dealer.hand.draw()
            action = 'Deal'
        elif not self.bettor.done:
            play = self.bettor.play()
            action = f'Bettor {play}'
        elif not self.dealer.done:
            play = self.dealer.play()
            action = f'Dealer {play}'
        else:
            action = 'Final'
        self.history.append(action)
        return action

    def save(self):
        os.makedirs(self.cache, exist_ok=True)
        fpath = f'{self.cache}/{self.fname}'
        # if os.path.exists(fpath):
        #     return
        with open(fpath, 'w') as fp:
            """Data to save:
                Card sequence
                Deal history
                Next to play
                Play options; for each:
                    Future state resulting from play action
                    If action involves taking a card, all future states with probability of each
            """
            done = self.dealer.done
            nxt = self.next_to_play
            if done:
                pdf = None
                net = self.bettor.net
            else:
                pdf = dict(zip(self.shoe.card_chars, self.shoe.pdf()))
                net = None

            options = {
                'Bettor': self.bettor.hand.options(),
                'Dealer': self.dealer.hand.options(),
            }

            data = {
                'Cards': self.cards,
                'History': self.history + [self.state],
                'Net': net,
                'Next': nxt,
                'Pdf': pdf,
                'Options': options,
            }
            json.dump(data, fp, indent=2)
