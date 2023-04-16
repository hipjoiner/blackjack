import json
import os

from config import home_dir
from hand import Hand
from rules import Rules
from shoe import Shoe


class Deal:
    saves = 0

    def __init__(
        self,
        rules=(1.5, 6, False, 'Any2', 3, True, True, True),
        dealer_hand=((0, 0, 0, 0, 0, 0, 0, 0, 0, 0), False, False, False),
        player_hands=(((0, 0, 0, 0, 0, 0, 0, 0, 0, 0), False, False, False),)
    ):
        self.rules = Rules(*rules)
        self.shoe = Shoe(self)
        self.dealer = Hand(self, 'D', *dealer_hand)
        self.player = [Hand(self, 'P', *ph) for ph in player_hands]
        self.saves = 0

    def __repr__(self):
        return self.implied_name

    @property
    def fpath(self):
        p = f'{home_dir}/states/{self.implied_name}.json'
        return p

    @staticmethod
    def from_cards(cards):
        d = Deal()
        for c in cards:
            d = d.new_deal(c)
        return d

    @property
    def implied_name(self):
        return f'{self.rules.implied_name} {str(self.dealer)} {" ".join(str(h) for h in self.player)}'

    @property
    def is_terminal(self):
        return self.next_hand is None

    def load(self):
        if not os.path.isfile(self.fpath):
            return None
        with open(self.fpath, 'r') as fp:
            contents = json.load(fp)
        return contents['deal']

    def new_deal(self, card):
        dealer_hand = self.dealer
        player_hands = self.player.copy()
        index = self.next_hand_index
        hand = self.next_hand.new_hand(card=card)
        if index is None:
            dealer_hand = hand
        else:
            player_hands[index] = hand
        return Deal(
            rules=self.rules.instreams,
            dealer_hand=dealer_hand.instreams,
            player_hands=tuple(ph.instreams for ph in player_hands)
        )

    @property
    def next_hand(self):
        # Deal phase
        if self.player[0].num_cards == 0:
            return self.player[0]
        if self.dealer.num_cards == 0:
            return self.dealer
        if self.player[0].num_cards == 1:
            return self.player[0]
        if self.dealer.num_cards == 1:
            return self.dealer

        # Check for Blackjacks phase
        if self.dealer.is_blackjack:
            return None
        if self.player[0].is_blackjack:
            return None

        # If player all busted, dealer doesn't play
        player_all_busted = True
        for h in self.player:
            if not h.is_busted:
                player_all_busted = False
        if player_all_busted:
            return None

        for h in self.player:
            if not h.is_terminal:
                return h
        if not self.dealer.is_terminal:
            return self.dealer
        return None

    @property
    def next_hand_index(self):
        h = self.next_hand
        if h == self.dealer:
            return None
        for i, ph in enumerate(self.player):
            if h == ph:
                return i
        return None

    @property
    def next_hand_options(self):
        if self.next_hand is None:
            return None
        return self.next_hand.options

    @property
    def next_states(self):
        if self.next_hand_options is None:
            return None
        states = {}
        for opt in self.next_hand_options:
            opt_states = {}
            if opt == 'Deal':
                for card, prob in self.shoe.pdf.items():
                    nd = self.new_deal(card)
                    if Deal.saves < 10000 and not os.path.isfile(nd.fpath):
                        nd.save()
                        Deal.saves += 1
                    opt_states[card] = {
                        'state': nd.implied_name,
                        'prob': prob,
                    }
            states[opt] = opt_states
        return states

    def save(self):
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
        with open(self.fpath, 'w') as fp:
            json.dump(self.state, fp, indent=4)

    @property
    def splits(self):
        return len(self.player) - 1

    @property
    def state(self):
        if self.is_terminal:
            round_data = {
                'terminal': self.is_terminal,
                'value': self.value,
            }
        else:
            round_data = {
                'next_hand': str(self.next_hand),
                'next_hand_index': self.next_hand_index,
                'options': self.next_hand_options,
                'next_states': self.next_states,
            }
        return {
            'state': self.implied_name,
            'round': round_data,
            'player': [h.state for h in self.player],
            'dealer': self.dealer.state,
            'rules': self.rules.implied_name,
            'shoe': {
                'cards': self.shoe.cards,
                'pdf': self.shoe.pdf,
            },
        }

    @property
    def value(self):
        val = 0
        for h in self.player:
            val += h.value
        return val


if __name__ == '__main__':
    deal = Deal.from_cards('A5T')
    deal.save()
