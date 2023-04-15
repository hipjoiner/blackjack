import json
import os

from config import home_dir
from hand import Hand
from rules import Rules
from shoe import Shoe


class Deal:
    def __init__(self, rules=None, dealer_hand=None, player_hands=None):
        self.rules = rules
        if self.rules is None:
            self.rules = Rules()
        self.dealer_hand = dealer_hand
        if self.dealer_hand is None:
            self.dealer_hand = Hand(self, 'D')
        self.player_hands = player_hands
        if self.player_hands is None:
            self.player_hands = [Hand(self, 'P')]
        self.shoe = Shoe(self.rules.decks)

    def __repr__(self):
        return self.implied_name

    @property
    def fpath(self):
        p = f'{home_dir}/states/{self.implied_name}.json'
        return p

    @property
    def implied_name(self):
        return f'{self.rules} # D {self.dealer_hand} # P {" ".join(str(h) for h in self.player_hands)}'

    def load(self):
        if not os.path.isfile(self.fpath):
            return None
        with open(self.fpath, 'r') as fp:
            contents = json.load(fp)
        return contents['deal']

    @property
    def next_hand(self):
        if self.dealer_hand.is_blackjack:
            return None
        for h in self.player_hands:
            if not h.is_terminal:
                return h
        if not self.dealer_hand.is_terminal:
            return self.dealer_hand
        return None

    @property
    def next_hand_index(self):
        h = self.next_hand
        if h == self.dealer_hand:
            return None
        for i, ph in enumerate(self.player_hands):
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
                    nh = self.next_hand.new_hand(cards=c)
                    opt_states[c] = {
                        'state': nh.implied_name,
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
        return len(self.player_hands) - 1

    @property
    def state(self):
        return {
            'state': self.implied_name,
            'rules': self.rules.state,
            'round': {
                'next_hand': self.next_hand_index,
                'options': self.next_hand_options,
                'next_states': self.next_states,
            },
            'shoe': self.shoe.pdf,
            'dealer': self.dealer_hand.state,
            'player': [h.state for h in self.player_hands],
        }


if __name__ == '__main__':
    d = Deal()
    d.save()
