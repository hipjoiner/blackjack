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
        return self.state()

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
            return ''
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
        return f'{self.state()}.txt'

    @property
    def next_hand(self):
        """Return reference to next hand to play, or None if all hands are done"""
        player = self.next_player
        for i, hand in enumerate(player.hands):
            if not hand.done:
                return hand
        return None

    @property
    def next_player(self):
        """Return reference to next player to play, or None if all players are done"""
        # Dealing phase
        if self.bettor.hand.num_cards == 0:
            return self.bettor
        if self.dealer.hand.num_cards == 0:
            return self.dealer
        if self.bettor.hand.num_cards == 1:
            return self.bettor
        if self.dealer.hand.num_cards == 1:
            return self.dealer
        if self.dealer.hand.can_peek:
            return self.dealer
        # After deal
        for i, hand in enumerate(self.bettor.hands):
            if not hand.done:
                return self.bettor
        if not self.dealer.done:
            return self.dealer
        return None

    @property
    def next_to_play(self):
        """Determine player and hand having next option to play; None if hand is complete."""
        # Dealing phase
        if self.bettor.hand.num_cards == 0:
            return 'Bettor 1'
        if self.dealer.hand.num_cards == 0:
            return 'Dealer'
        if self.bettor.hand.num_cards == 1:
            return 'Bettor 1'
        if self.dealer.hand.num_cards == 1:
            return 'Dealer'
        if self.dealer.hand.can_peek:
            return 'Dealer'
        # After deal, straightforward
        for i, hand in enumerate(self.bettor.hands):
            if not hand.done:
                return f'Bettor {i + 1}'
        if not self.dealer.done:
            return 'Dealer'
        return None

    @property
    def num_cards(self):
        return len(self.cards)

    @property
    def shoe(self):
        return self.table.shoe

    def clear(self):
        self.dealer.clear()
        self.bettor.clear()

    def run(self):
        """Run 1 step of a deal."""
        self.history.append(self.state())
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
            to_play = self.next_to_play
            net = None
            pdf = None
            if done:
                net = self.bettor.net
            else:
                pdf = self.shoe.card_pdf()
            options = self.next_player.hand.options()
            opt_pdfs = {}
            for option in options:
                if self.next_hand:
                    next_hands = self.next_hand.next_states(option)
                    next_states = {}
                    for h, prob in next_hands.items():
                        if to_play.startswith('Dealer'):
                            next_state = self.state(dealer_hand=h)
                        else:
                            # FIXME: This won't work with multiple (split) bettor hands in play
                            next_state = self.state(bettor_hands=[h])
                        next_states[next_state] = prob
                    opt_pdfs[option] = next_states
                else:
                    opt_pdfs[option] = ''

            data = {
                'Cards': self.cards,
                'History': self.history + [self.state()],
                'Net': net,
                'Next': to_play,
                'Pdf': pdf,
                'Options': {
                    to_play: opt_pdfs
                },
            }
            json.dump(data, fp, indent=2)

    def state(self, dealer_hand=None, bettor_hands=None):
        if dealer_hand:
            d = dealer_hand
        else:
            d = str(self.dealer.hand)
            if d == 'None':
                d = ''
        if bettor_hands:
            b = bettor_hands
        else:
            b = [f'{str(h)}' for h in self.bettor.hands]
            if not b:
                b = ['']
        return '-'.join(['Deal'] + [d] + b)
