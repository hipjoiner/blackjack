import json

from config import cache


class Rules:
    def __init__(self, name):
        self.name = name
        with open(self.fpath, 'r') as fp:
            self.spec = json.load(fp)

    def __str__(self):
        return self.name

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
    def dealer_hits_soft_17(self):
        return self.spec['dealer_hits_soft_17']

    @property
    def double_allowed(self):
        return self.spec['double_allowed']

    @property
    def double_after_split(self):
        return self.spec['double_after_split']

    @property
    def split_2_to_10(self):
        return self.spec['split_2_to_10']

    @property
    def split_aces(self):
        return self.spec['split_aces']

    @property
    def split_aces_draw(self):
        return self.spec['split_aces_draw']

    @property
    def surrender(self):
        return self.spec['surrender']
