"""
Complete player strategy answers these questions in order:
    Should I surrender?
    Should I split?
    Should I double?
    Should I hit?
"""
import json

from config import cache


class Strategy:
    def __init__(self, name):
        self.name = name
        with open(self.fpath, 'r') as fp:
            self.spec = json.load(fp)

    @property
    def fpath(self):
        return f'{cache}/strategies/{self.name}.json'

    @staticmethod
    def case_check(cases, key, dlr_up):
        if key in cases:
            if type(cases[key]) == bool:
                return cases[key]
            if dlr_up in cases[key]:
                return True
        return False

    def play(self, hand, dlr_up):
        if self.surrender(hand, dlr_up):
            return 'surrender'
        if self.split(hand, dlr_up):
            return 'split'
        if self.double(hand, dlr_up):
            return 'double'
        if self.hit(hand, dlr_up):
            return 'hit'
        return 'stand'

    def surrender(self, hand, dlr_up):
        cases = self.spec['surrender']
        key = str(hand.total)
        return self.case_check(cases, key, dlr_up)

    def split(self, hand, dlr_up):
        cases = self.spec['split']
        key = hand.cards
        return self.case_check(cases, key, dlr_up)

    def double(self, hand, dlr_up):
        if hand.soft:
            hand_type = 'soft'
        else:
            hand_type = 'hard'
        cases = self.spec['double'][hand_type]
        key = str(hand.total)
        return self.case_check(cases, key, dlr_up)

    def hit(self, hand, dlr_up):
        if hand.soft:
            hand_type = 'soft'
        else:
            hand_type = 'hard'
        cases = self.spec['hit'][hand_type]
        key = str(hand.total)
        return self.case_check(cases, key, dlr_up)
