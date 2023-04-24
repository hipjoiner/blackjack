from config import card_symbols, card_values, card_indexes


class Hand:
    def __init__(
        self,
        deal,
        player,
        counts=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        surrendered=False,
        split_card='',
        split_count=0,
        doubled=False,
        stand=False
    ):
        self.deal = deal
        self.player = player
        self.counts = counts
        self.surrendered = surrendered
        self.split_card = split_card
        self.split_count = split_count
        self.doubled = doubled
        self.stand = stand

    def __lt__(self, other):
        return self.implied_name < other.implied_name

    def __str__(self):
        return self.implied_name

    @property
    def actions(self):
        if self.surrendered or self.doubled or self.stand or self.total >= 21:
            return None
        if self.can_deal:
            return ['Deal']
        if self.can_turn:
            return ['Turn']
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
    def can_double(self):
        if self.is_dealer:
            return False
        if self.surrendered or self.doubled or self.stand:
            return False
        if self.num_cards != 2:
            return False
        if self.split_count > 0 and not self.deal.rules.double_after_split:
            return False
        # For efficiency, never let anyone (i.e., Player) do anything as stupid as the below
        if self.hard_total >= 13:
            return False
        if self.total >= 20:
            return False
        return True

    @property
    def can_hit(self):
        if self.is_dealer:
            if self.can_turn:
                return False
            if self.total <= 16:
                return True
            if self.deal.rules.hit_soft_17 and self.total == 17 and self.is_soft:
                return True
            return False
        if self.surrendered or self.doubled or self.stand:
            return False
        if self.split_count > 0 and self.split_card == 'A':
            return False
        # For efficiency, never let anyone (i.e., Player) do anything as stupid as the below
        if self.hard_total >= 18:
            return False
        if self.total >= 20:
            return False
        return True

    @property
    def can_split(self):
        if self.is_dealer:
            return False
        if not self.is_pair:
            return False
        if self.split_count > 0 and self.split_card == 'A' and not self.deal.rules.resplit_aces:
            return False
        if self.split_count >= self.deal.rules.splits_allowed:
            return False
        return True

    @property
    def can_stand(self):
        if self.is_dealer:
            return not self.can_turn and not self.can_hit
        if self.surrendered or self.doubled or self.stand:
            return False
        return True

    @property
    def can_surrender(self):
        if self.is_dealer:
            return False
        if self.surrendered or self.split_count > 0 or self.doubled or self.stand:
            return False
        if self.total < 12:         # For efficiency, don't let Player do something this stupid
            return False
        return self.num_cards == 2

    @property
    def can_turn(self):
        return self.is_dealer and self.counts[card_indexes['x']] > 0

    @property
    def cards(self):
        # Shorthand representation for viewing
        cstr = ''
        for i in [9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 10]:    # Sort Aces first, tens last, down card very last, just for aesthetics
            cstr += card_symbols[i] * int(self.counts[i])
        return cstr

    @property
    def hard_total(self):
        return sum([self.counts[i] * card_values[i] for i in card_indexes.values()])

    @property
    def implied_name(self):
        mods = ''
        if self.surrendered:
            mods += 'R'
        if self.doubled:
            mods += 'D'
        if self.stand:
            mods += 'S'
        if self.split_card:
            mods += f'V{self.split_card}x{self.split_count}'
        if mods:
            return self.cards + '^' + mods
        return self.cards

    @property
    def instreams(self):
        return tuple(self.counts), self.surrendered, self.split_card, self.split_count, self.doubled, self.stand

    @property
    def is_blackjack(self):
        if self.num_cards == 2 and self.total == 21:
            if self.is_dealer or self.split_count == 0:
                return True
        return False

    @property
    def is_busted(self):
        return self.total > 21

    @property
    def is_dealer(self):
        return self.player == 'Dealer'

    @property
    def is_decided(self):
        if self.deal.dealer.num_cards < 2:
            return False
        if self.is_blackjack or self.deal.dealer.is_blackjack:
            return True
        if self.is_busted or self.surrendered:
            return True
        return self.is_done and self.deal.dealer.is_done

    @property
    def is_done(self):
        return self.actions is None

    @property
    def is_pair(self):
        return self.num_cards == 2 and max(self.counts) == 2

    @property
    def is_soft(self):
        return self.total != self.hard_total

    def new_hand(
        self,
        card='',
        surrendered=None,
        split=None,
        doubled=None,
        stand=None
    ):
        counts = list(self.counts)
        split_card = self.split_card
        split_count = self.split_count
        if split:
            i = None
            for i, count in enumerate(counts):
                if count == 2:
                    break
            split_card = card_symbols[i]
            split_count = self.split_count + 1
            counts = [c / 2 for c in counts]
        if card:
            counts[card_indexes[card]] += 1
            if card != 'x':
                counts[card_indexes['x']] = 0
        sur = self.surrendered if surrendered is None else surrendered
        dbl = self.doubled if doubled is None else doubled
        std = self.stand if stand is None else stand
        new_hand = Hand(
            deal=self.deal,
            player=self.player,
            counts=tuple(counts),
            surrendered=sur,
            split_card=split_card,
            split_count=split_count,
            doubled=dbl,
            stand=std
        )
        return new_hand

    @property
    def num_cards(self):
        return sum(self.counts)

    @property
    def outcome(self):
        if not self.is_decided:
            return None
        dealer = self.deal.dealer
        if self.is_blackjack:
            if dealer.is_blackjack:
                return 'Push'
            return 'Blackjack'
        if self.surrendered:
            return 'Surrender'
        if dealer.is_blackjack:
            return 'Lose'
        if self.is_busted:
            return 'Bust'
        if dealer.is_busted:
            return 'Win'
        if self.total > dealer.total:
            return 'Win'
        if self.total < dealer.total:
            return 'Lose'
        return 'Push'

    @property
    def state(self):
        return {
            'cards': self.cards,
            'total': self.total,
            'is_done': self.is_done,
            'surrendered': self.surrendered,
            'split_card': self.split_card,
            'split_count': self.split_count,
            'doubled': self.doubled,
            'stand': self.stand,
            'is_blackjack': self.is_blackjack,
            'is_busted': self.is_busted,
            'is_decided': self.is_decided,
            'is_soft': self.is_soft,
            'outcome': self.outcome,
            'value': self.value,
        }

    @property
    def total(self):
        """Compute the best point total for the hand."""
        if self.hard_total <= 11 and self.counts[card_indexes['A']] > 0:
            return self.hard_total + 10
        return self.hard_total

    @property
    def valuation_leaf(self):
        """If this hand is terminal and outcome can be known, then return the outcome and bet value.
            Otherwise, return nothing.
        """
        if self.value is None:
            return None
        return {
            'outcome': self.outcome,
            'value': self.value,
        }

    @property
    def value(self):
        """If this hand is terminal and outcome can be known, compute the bet return to the Player."""
        if self.outcome is None:
            return None
        if self.outcome == 'Blackjack':
            return self.deal.rules.blackjack_pays
        if self.outcome == 'Surrender':
            return -0.5
        if self.outcome == 'Win':
            val = 1.0
        elif self.outcome in ['Bust', 'Lose']:
            val = -1.0
        else:
            val = 0.0
        if self.doubled:
            val *= 2.0
        if self.split_count:
            val *= (self.split_count + 1.0)
        return val


if __name__ == '__main__':
    # h = Hand(Rules(), 'Player', cards='AT')
    # print(f'Hand:\n{h}')
    # print(f'Hand data:\n{h.state}')
    pass
