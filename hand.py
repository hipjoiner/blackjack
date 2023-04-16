from config import CachedInstance


class Hand:
    symbols = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A']
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
    indexes = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'A': 9}

    def __init__(self, deal, player, counts=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0), showing='', surrendered=False, doubled=False, stand=False):
        self.deal = deal
        self.player = player
        self.counts = counts
        self.showing = showing
        self.surrendered = surrendered
        self.doubled = doubled
        self.stand = stand

    def __str__(self):
        return self.implied_name

    @property
    def actions(self):
        if self.is_maxed or self.surrendered or self.doubled or self.stand:
            return None
        if self.can_deal:
            return ['Deal']
        acts = []
        if self.can_surrender:
            acts.append('Surrender')
        if self.can_split:
            acts.append('Split')
        if self.can_double:
            acts.append('Double')
        if self.can_hit:
            acts.append('Hit')
        if self.can_stand:
            acts.append('Stand')
        if not acts:
            return None
        return acts

    @property
    def can_deal(self):
        return self.num_cards < 2

    @property
    def can_surrender(self):
        if self.is_dealer:
            return False
        if self.surrendered or self.doubled or self.stand:
            return False
        return self.num_cards == 2 and self.deal.splits == 0

    @property
    def can_split(self):
        if self.is_dealer:
            return False
        return self.is_pair and self

    @property
    def can_double(self):
        if self.is_dealer:
            return False
        if self.surrendered or self.doubled or self.stand:
            return False
        if self.num_cards != 2:
            return False
        return True

    @property
    def can_hit(self):
        if self.is_dealer:
            if self.total <= 16:
                return True
            if self.deal.rules.hit_soft_17 and self.total == 17 and self.is_soft:
                return True
            return False
        if self.surrendered or self.doubled or self.stand:
            return False
        return True

    @property
    def can_stand(self):
        if self.is_dealer:
            return not self.can_hit
        if self.surrendered or self.doubled or self.stand:
            return False
        return True

    @property
    def cards(self):
        # Shorthand representation for viewing
        cstr = ''
        for i, c in enumerate(self.counts):
            cstr += self.symbols[i] * c
        return cstr

    @property
    def hard_total(self):
        return sum([self.counts[i] * self.values[i] for i in self.indexes.values()])

    @property
    def implied_name(self):
        s = '-'.join([str(c) for c in self.counts])
        extra = ''
        if self.showing:
            extra += self.showing
        if self.surrendered:
            extra += 'R'
        elif self.doubled:
            extra += 'D'
        if self.stand:
            extra += 'S'
        if extra:
            s = extra + '^' + s
        return s

    @property
    def instreams(self):
        return tuple(self.counts), self.showing, self.surrendered, self.doubled, self.stand

    @property
    def is_blackjack(self):
        if self.num_cards == 2 and self.total == 21:
            if self.is_dealer or self.splits == 0:
                return True
        return False

    @property
    def is_busted(self):
        return self.total > 21

    @property
    def is_dealer(self):
        return self.player == 'D'

    @property
    def is_decided(self):
        if self.is_blackjack or self.deal.dealer.is_blackjack:
            return True
        if self.is_busted or self.surrendered:
            return True
        return self.is_terminal and self.deal.dealer.is_terminal

    @property
    def is_maxed(self):
        return self.total >= 21

    @property
    def is_pair(self):
        return self.num_cards == 2 and max(self.counts) == 2

    @property
    def is_soft(self):
        return self.total != self.hard_total

    @property
    def is_terminal(self):
        return self.actions is None

    def new_hand(self, card='', surrendered=None, doubled=None, stand=None):
        counts = list(self.counts)
        if card:
            counts[self.indexes[card]] += 1
        if surrendered is None:
            surrendered = self.surrendered
        if doubled is None:
            doubled = self.doubled
        if stand is None:
            stand = self.stand
        new_hand = Hand(deal=self.deal, player=self.player, counts=tuple(counts), surrendered=surrendered, doubled=doubled, stand=stand)
        return new_hand

    @property
    def num_cards(self):
        return sum(self.counts)

    @property
    def splits(self):
        return self.deal.splits

    @property
    def state(self):
        return {
            'cards': self.cards,
            'surrendered': self.surrendered,
            'doubled': self.doubled,
            'stand': self.stand,
            'total': self.total,
            'is_blackjack': self.is_blackjack,
            'is_busted': self.is_busted,
            'is_decided': self.is_decided,
            'is_soft': self.is_soft,
            'is_terminal': self.is_terminal,
            'winner': self.winner,
            'value': self.value,
        }

    @property
    def total(self):
        if self.hard_total <= 11 and self.counts[self.indexes['A']] > 0:
            return self.hard_total + 10
        return self.hard_total

    @property
    def value(self):
        if self.winner is None:
            return None
        if self.winner == 'Player':
            if self.is_blackjack:
                return self.deal.rules.blackjack_pays
            if self.doubled:
                return 2.0
            return 1.0
        if self.winner == 'Dealer':
            if self.surrendered:
                return -0.5
            if self.doubled:
                return -2.0
            return -1.0
        return 0.0

    @property
    def winner(self):
        if not self.is_decided:
            return None
        dealer = self.deal.dealer
        if self.is_blackjack:
            if dealer.is_blackjack:
                return 'Push'
            return 'Player'
        if self.surrendered:
            return 'Dealer'
        if dealer.is_blackjack:
            return 'Dealer'
        if self.is_busted:
            return 'Dealer'
        if dealer.is_busted:
            return 'Player'
        if self.total > dealer.total:
            return 'Player'
        if self.total < dealer.total:
            return 'Dealer'
        return 'Push'


if __name__ == '__main__':
    # h = Hand(Rules(), 'P', cards='AT')
    # print(f'Hand:\n{h}')
    # print(f'Hand data:\n{h.state}')
    pass
