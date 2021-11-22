"""
Complete player strategy answers these questions in order:
    Should I surrender?
    Should I split?
    Should I double?
    Should I hit?
"""
import json

from config import cache


def case_check(cases, key, dealer_up):
    if key in cases:
        if type(cases[key]) == bool:
            return cases[key]
        if dealer_up in cases[key]:
            return True
    return False


class Strategy:
    def __init__(self, name):
        self.name = name
        with open(self.fpath, 'r') as fp:
            self.spec = json.load(fp)

    @property
    def fpath(self):
        return f'{cache}/strategies/{self.name}.json'

    def play(self, hand, dealer_up):
        if self.surrender(hand, dealer_up):
            return 'surrender'
        if self.split(hand, dealer_up):
            return 'split'
        if self.double(hand, dealer_up):
            return 'double'
        if self.hit(hand, dealer_up):
            return 'hit'
        return 'stand'

    def surrender(self, hand, dealer_up):
        cases = self.spec['surrender']
        key = str(hand.total)
        return case_check(cases, key, dealer_up)

    def split(self, hand, dealer_up):
        cases = self.spec['split']
        key = hand.cards
        return case_check(cases, key, dealer_up)

    def double(self, hand, dealer_up):
        if hand.is_soft:
            hand_type = 'soft'
        else:
            hand_type = 'hard'
        cases = self.spec['double'][hand_type]
        key = str(hand.total)
        return case_check(cases, key, dealer_up)

    def hit(self, hand, dealer_up):
        if hand.is_soft:
            hand_type = 'soft'
        else:
            hand_type = 'hard'
        cases = self.spec['hit'][hand_type]
        key = str(hand.total)
        return case_check(cases, key, dealer_up)
