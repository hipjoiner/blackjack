from pprint import pprint


class Shoe:
    ranks = 'TA23456789'

    def __init__(self, decks, preset=''):
        self.decks = decks
        self.preset = preset
        self.dealt = ''

    def __str__(self):
        return f'{self.decks}-deck shoe'

    @property
    def cards_left(self):
        result = {}
        for rank in self.ranks:
            if rank == 'T':
                rank_tot = self.decks * 4 * 4
            else:
                rank_tot = self.decks * 4
            rank_dealt = self.dealt.count(rank)
            result[rank] = rank_tot - rank_dealt
        return result

    @property
    def pdf(self):
        tot_cards_left = self.decks * 52 - len(self.dealt)
        return dict(zip(self.ranks, [self.cards_left[rank] / tot_cards_left for rank in self.ranks]))

    @property
    def state(self):
        return {
            'decks': self.decks,
            'preset': self.preset,
            'dealt': self.dealt,
            'pdf': self.pdf,
            # 'cards_left': self.cards_left,
        }

    def get_card(self):
        num_dealt = len(self.dealt)
        card = self.preset[num_dealt]
        self.dealt = f'{self.dealt}{card}'
        return card


if __name__ == '__main__':
    s = Shoe(8, 'T5A')
    print(s)
    s.get_card()
    s.get_card()
    pprint(s.state())
