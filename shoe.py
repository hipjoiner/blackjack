import numpy as np

from config import card_symbols, card_indexes


class Shoe:
    def __init__(self, deal):
        self.deal = deal
        self.decks = deal.rules.shoe_decks
        rank_count = self.decks * 4
        ten_count = rank_count * 4
        unknown_count = 0
        self.base_counts = [
            rank_count,             # 2s
            rank_count,             # 3s
            rank_count,             # 4s
            rank_count,             # 5s
            rank_count,             # 6s
            rank_count,             # 7s
            rank_count,             # 8s
            rank_count,             # 9s
            ten_count,              # Ts
            rank_count,             # As
            unknown_count,          # Down cards
        ]

    @property
    def cards(self):
        return dict(zip(card_symbols, self.counts))

    @property
    def cards_out(self):
        outs = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        outs += self.deal.dealer.counts
        for h in self.deal.player:
            outs += h.counts
        # FIXME: Is this math exactly correct for cases where Dealer does actually have a down card?
        # If he does, with A showing, then there is really some non-T card out, which impacts probabilities
        outs[10] = 0        # By convention, there are never any Unknown (x) cards out, or in the shoe
        return outs

    @property
    def counts(self):
        c = self.base_counts - self.cards_out
        return c.tolist()

    @property
    def num_cards(self):
        return sum(self.counts)

    @property
    def pdf(self):
        probs = [self.counts[i] / self.num_cards if self.num_cards != 0 else 0 for i in card_indexes.values()]
        return dict(zip(card_symbols, probs))


if __name__ == '__main__':
    pass
