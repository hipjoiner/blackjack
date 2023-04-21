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
        outs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i, count in enumerate(self.deal.dealer.counts):
            outs[i] += count
        for h in self.deal.player:
            for i, count in enumerate(h.counts):
                outs[i] += count
        outs[10] = 0        # By convention, there are never any Unknown (x) cards out, or in the shoe
        return outs

    @property
    def counts(self):
        c = self.base_counts.copy()
        for i, count in enumerate(self.cards_out):
            c[i] -= count
        return c

    @property
    def num_cards(self):
        return sum(self.counts)

    @property
    def pdf(self):
        probs = [self.counts[i] / self.num_cards if self.num_cards != 0 else 0 for i in card_indexes.values()]
        return dict(zip(card_symbols, probs))


if __name__ == '__main__':
    pass
