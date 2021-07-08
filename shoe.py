"""
Parameters defining a complete shoe configuration:
    Decks: 1-8
"""
import random
from rules import shoe_decks


class Shoe:
    card_chars = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T']

    def __init__(self, decks=8):
        self.decks = decks
        self.cards = self.decks * 52
        self.cards_drawn = None
        self.cards_left = None
        self.shuffle()

    def __str__(self):
        return shoe_decks[self.decks]

    def card(self, rank):
        return self.card_chars[rank]

    def cdf(self):
        tot_cards_left = sum(self.cards_left)
        result = [0.0] * 10
        c = 0
        for rank in range(10):
            p = self.cards_left[rank] / tot_cards_left
            c = c + p
            result[rank] = c
        return result

    def choose_random(self):
        """Choose a random card from what's left in the shoe"""
        cdf = self.cdf()
        r = random.random()
        for rank in range(10):
            if r < cdf[rank]:
                return rank
        raise ValueError(f'Choose random failed: seed {r}, cdf {cdf}')

    def depleted(self):
        """For now, we'll say 10% of shoe remaining is depleted; time to reshuffle"""
        return sum(self.cards_left) < self.cards / 10

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

    def shuffle(self):
        self.cards_left = [4 * self.decks] * 9 + [4 * self.decks * 4]
        self.cards_drawn = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
