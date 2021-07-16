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
        return self.status

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
        return f'Cards-{self.cards}.txt'

    @property
    def num_cards(self):
        return len(self.cards)

    @property
    def shoe(self):
        return self.table.shoe

    @property
    def status(self):
        if self.dealer.num_hands == 0:
            return ''
        c = f'Cards-{self.cards}'
        if not self.dealer.hand:
            return c
        if not self.dealer.hand.revealed:
            dstr = f'{self.dealer} (?)'
        else:
            dstr = f'{self.dealer} ({self.dealer.hand.total})'
        bstr = '_'.join([f'{h} ({h.total})' for h in self.bettor.hands])
        t = f'Dealer-{dstr}; Bettor-{bstr}'
        return f'{c}; {t}'

    def run(self):
        """Run 1 step of a deal."""
        action = ''
        self.history.append(self.status)
        if self.dealer.num_hands == 0:
            self.bettor.add_hand()
            self.dealer.add_hand()
            self.dealer.hand.revealed = False
            return ''
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
        if action:
            self.history.append(action)
        return action

    def save(self):
        os.makedirs(self.cache, exist_ok=True)
        fpath = f'{self.cache}/{self.fname}'
        # if os.path.exists(fpath):
        #     return
        with open(fpath, 'w') as fp:
            """Data to save:
                Cards total
                Dealer cards
                Player cards
                All possible next play actions
                    Future state resulting from play action
                    If action involves taking a card, all future states with probability of each
            """
            done = self.dealer.done
            if done:
                nxt = None
                net = self.bettor.net
            else:
                nxt = dict(zip(self.shoe.card_chars, self.shoe.pdf()))
                net = None

            data = {
                'Cards': self.cards,
                'Play': self.history + [self.status],
                'Final': done,
                'Net': net,
                'Next': nxt,
            }
            json.dump(data, fp, indent=2)
