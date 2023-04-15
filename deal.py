import json
import os

from config import home_dir
from hand import Hand
from rules import Rules
from shoe import Shoe


class Deal:
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

    @property
    def implied_name(self):
        return f'{self.rules.implied_name} {str(self.dealer)} {" ".join(str(h) for h in self.player)}'

    def load(self):
        if not os.path.isfile(self.fpath):
            return None
        with open(self.fpath, 'r') as fp:
            contents = json.load(fp)
        return contents['deal']

    def new_deal(self, index, hand):
        dealer_hand = self.dealer
        player_hands = self.player.copy()
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
        if self.dealer.is_blackjack:
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
                for c, p in self.shoe.pdf.items():
                    nh = self.next_hand.new_hand(card=c)
                    nd = self.new_deal(self.next_hand_index, nh)
                    if self.saves < 100:
                        nd.save()
                        self.saves += 1
                    opt_states[c] = {
                        'state': nd.implied_name,
                        'prob': p,
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
        return {
            'state': self.implied_name,
            'rules': self.rules.implied_name,
            'round': {
                'next_hand': self.next_hand_index,
                'options': self.next_hand_options,
                'next_states': self.next_states,
            },
            'shoe': self.shoe.pdf,
            'dealer': self.dealer.state,
            'player': [h.state for h in self.player],
        }


if __name__ == '__main__':
    d = Deal()
    d.save()
