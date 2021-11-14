import random


class Shoe:
    card_chars = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T']

    def __init__(self, decks):
        self.decks = decks
        self.cards = self.decks * 52
        self.cards_drawn = None
        self.cards_left = None
        self.deal_sequence = ''
        self.shuffle()

    def __str__(self):
        return self.name

    @property
    def name(self):
        return f'{self.decks}-deck shoe'

    def card(self, rank):
        """Return character representation of card, given numerical rank"""
        return self.card_chars[rank]

    def card_pdf(self):
        """Return dict by card character giving draw probability from pdf"""
        return dict(zip(self.card_chars, self.pdf()))

    def cdf(self):
        result = [0.0] * 10
        c = 0
        for rank in range(10):
            c = c + self.pdf()[rank]
            result[rank] = c
        return result

    def pdf(self):
        """Array of probabilities of draw, ordered by rank"""
        tot_cards_left = sum(self.cards_left)
        return [self.cards_left[rank] / tot_cards_left for rank in range(10)]

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
        dealt = self.card(rank)
        self.deal_sequence = f'{self.deal_sequence}{dealt}'
        return dealt

    def shuffle(self):
        self.cards_left = [4 * self.decks] * 9 + [4 * self.decks * 4]
        self.cards_drawn = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
