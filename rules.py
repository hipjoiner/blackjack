import json

from config import cache


class Rules:
    def __init__(self, name):
        self.name = name
        with open(self.fpath, 'r') as fp:
            self.spec = json.load(fp)

    @property
    def fpath(self):
        return f'{cache}/rules/{self.name}.json'

    @property
    def blackjack_pays(self):
        return self.spec['blackjack_pays']

    @property
    def dealer_peeks_for_blackjack(self):
        return self.spec['dealer_peeks_for_blackjack']

    @property
    def double_allowed(self):
        return self.spec['double_allowed']

    @property
    def double_after_split_allowed(self):
        return self.spec['double_after_split_allowed']

    @property
    def times_split_2_to_10(self):
        return self.spec['times_split_2_to_10']

    @property
    def times_split_aces(self):
        return self.spec['times_split_aces']

    @property
    def split_aces_draw_cards(self):
        return self.spec['split_aces_draw_cards']

    @property
    def surrender_allowed(self):
        return self.spec['surrender_allowed']

    @property
    def state(self):
        return {
            'blackjack_pays': self.blackjack_pays,
            'dealer_peeks_for_blackjack': self.dealer_peeks_for_blackjack,
            'double_allowed': self.double_allowed,
            'double_after_split_allowed': self.double_after_split_allowed,
            'times_split_2_to_10': self.times_split_2_to_10,
            'times_split_aces': self.times_split_aces,
            'split_aces_draw_cards': self.split_aces_draw_cards,
            'surrender_allowed': self.surrender_allowed,
        }

    def can_surrender(self, hand):
        """Only on first two cards, with surrender allowed"""
        if not self.surrender_allowed:
            return False
        if len(hand.cards) != 2:
            return False
        return True

    def can_split(self, hand):
        """On a pair, if not at maximum splits allowed"""
        if not hand.is_paired:
            return False
        if hand.cards[0] == 'A':
            return hand.splits < self.times_split_aces
        else:
            return hand.splits < self.times_split_2_to_10

    def can_double(self, hand):
        """Two cards, plus rules"""
        if self.double_allowed == 3:      # No double allowed
            return False
        if hand.num_cards != 2:
            return False
        if hand.splits > 0 and not self.double_after_split_allowed:
            return False
        if hand.splits > 0 and hand.cards[0] == 'A' and self.split_aces_draw_cards == 1:
            return False
        if self.double_allowed == 0:      # Double any 2
            return True
        if self.double_allowed == 1 and hand.total in [9, 10, 11]:
            return True
        if self.double_allowed == 2 and hand.total in [10, 11]:
            return True
        return False

    def can_hit(self, hand):
        if hand.is_doubled:
            return False
        if hand.splits > 0 and hand.cards[0] == 'A' and self.split_aces_draw_cards == 1:
            return False
        return hand.total < 21
