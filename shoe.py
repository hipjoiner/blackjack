"""
Parameters defining a complete shoe configuration:
    Decks: 1-8
"""
import random
from random import randint
from rules import shoe_decks


class Shoe:
    cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T']

    def __init__(self, decks=8):
        self.decks = decks
        self.cards_left = [decks, decks, decks, decks, decks, decks, decks, decks, decks, decks * 4]
        self.cards_drawn = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def __str__(self):
        return shoe_decks[self.decks]

    def cdf(self):
        cards = sum(self.cards_left)
        result = [0.0] * 10
        p = 0
        for rank in range(10):
            result[rank] = p + self.cards_left[rank] / cards
            p += result[rank]
        return result

    def choose_random(self):
        """Choose a random card from what's left in the shoe"""
        cdf = self.cdf()
        r = random.random()
        for rank in range(0, 10, -1):
            if r >= cdf[rank]:
                return rank
        raise ValueError(f'Choose random failed: seed {r}, cdf {cdf}')

    def card(self, rank):
        return self.cards[rank]

    def draw(self, rank=None):
        """Return a single card; update shoe state.
        If rank specified, return that specific rank (unless there are none; then error)
        If rank unspecified, return a card at random based on shoe state.
        """
        if rank is None:
            rank = self.choose_random()
        if self.cards_left[rank] == 0:
            raise ValueError(f'Trying to draw a {rank}, but there are none left')
        self.cards_left[rank] -= 1
        self.cards_drawn[rank] += 1
        return self.card(rank)

    def draws(self):
        """Return an array of probabilities for all card ranks"""
        pass
