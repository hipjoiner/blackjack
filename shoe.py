from config import card_symbols, card_indexes


class Shoe:
    def __init__(self, deal, true_count=0):
        self.deal = deal
        self.true_count = true_count
        self.decks = deal.rules.shoe_decks

    @property
    def base_count(self):
        rank_count = self.decks * 4
        ten_count = rank_count * 4
        unknown_count = 0
        counts = [
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
        for i in range(len(counts)):
            counts[i] -= self.true_count_adjust[i]
        return counts

    @property
    def cards(self):
        return dict(zip(card_symbols, self.counts))

    @property
    def cards_out(self):
        outs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i, count in enumerate(self.deal.dealer.counts):
            outs[i] += count
        for i, count in enumerate(self.deal.player.counts):
            outs[i] += count
        if self.deal.player.split_card:
            i = card_indexes[self.deal.player.split_card]
            outs[i] += self.deal.player.split_count
        outs[10] = 0        # By convention, there are never any Unknown (x) cards out, or in the shoe
        return outs

    @property
    def counts(self):
        c = self.base_count.copy()
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

    @property
    def true_count_adjust(self):
        """There are 10 ranks in a deck that contribute 1 or -1 to the count for the deck:
            2, 3, 4, 5, 6 are +1
            T, J, Q, K, A are -1
        So to change the true (per deck) count by exactly 1, we modify the count
        of each rank that contributes by 1/10 times the number of decks in the shoe.

        For example, to change the true count of a 6-deck shoe to +1, we would modify the rank counts as follows:
            2, 3, 4, 5, 6 start with rank counts 24 each.
                Adjust each by +6/10, for total adjustment of +6/10 * 5 or +3
            T, J, Q, K, A start with rank counts 96 for Ts and 24 for As.
                Adjust Ts by +6/10 * 4 or +2.4
                Adjust As by +6/10 or +0.6

        Total adjustment then is +3 +2.4 +0.6 = +6, for a 6-deck true count of +1.
        """
        base_adjustment = self.decks * self.true_count / 10.0
        adjs = [
            base_adjustment,        # 2s
            base_adjustment,        # 3s
            base_adjustment,        # 4s
            base_adjustment,        # 5s
            base_adjustment,        # 6s
            0,                      # 7s
            0,                      # 8s
            0,                      # 9s
            -base_adjustment * 4,   # Ts
            -base_adjustment,       # As
            0,                      # Down cards
        ]
        return adjs


if __name__ == '__main__':
    pass
