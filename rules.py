"""
Parameters defining a complete rules configuration:
    Table
        Blackjack pays:                     3-2, 7-5, 6-5, 1-1
        Shoe decks:                         1-8
    Dealer
        Dealer peeks for blackjack:         True/False
        Dealer hits soft 17:                True/False
    Player
        Doubling:                           any 2 cards, 9-11, 10-11, not allowed
        Split 2-10s:                        3 times, 2 times, 1 time, not allowed
        Split aces:                         3 times, 2 times, 1 time, not allowed
        Draw to split aces:                 1 only, any
        Double after split:                 True/False
        Surrender:                          any, any except ace, none
"""

blackjack_payoffs = {
    1.5: '3-2',
    1.4: '7-5',
    1.2: '6-5',
    1.0: '1-1',
}

shoe_decks = {
    1: '1Deck',
    2: '2Decks',
    3: '3Decks',
    4: '4Decks',
    5: '5Decks',
    6: '6Decks',
    7: '7Decks',
    8: '8Decks',
}

dealer_peek_options = {
    True: 'DlrPeek',
    False: 'DlrNoPk',
}

dealer_hit_options = {
    True: 'DlrHit17',
    False: 'DlrStnd17',
}

double_options = {
    0: 'DblAny2',
    1: 'Dbl9-11',
    2: 'Dbl10-11',
    3: 'NoDbls',
}

double_after_split_options = {
    True: 'DblSplt',
    False: 'NoDblSplt',
}

split_2_to_10_options = {
    0: 'NoSplt',
    1: 'Splt1',
    2: 'Splt2',
    3: 'Splt3',
}

split_aces_options = {
    0: 'NoSpltA',
    1: 'SpltA1',
    2: 'SpltA2',
    3: 'SpltA3',
}

split_aces_draw_options = {
    0: 'SpltADr',
    1: 'SpltA1Cd',
}

surrender_options = {
    0: 'SurAny',
    1: 'SurExA',
    2: 'NoSurr',
}


class Rules:
    def __init__(
        self,
        blackjack_pays=1.5,                 # Default: 3-to-2
        decks=8,                            # Default: 8 decks
        dealer_peeks_for_blackjack=True,    # Default: dealer peeks
        dealer_hits_soft_17=True,           # Default: dealer hits soft 17
        double_allowed=0,                   # Default: double any 2 cards
        double_after_split=True,            # Default: double after split allowed
        split_2_to_10=3,                    # Default: split up to 3 times
        split_aces=1,                       # Default: split aces once only
        split_aces_draw=1,                  # Default: split aces get 1 card only
        surrender=0                         # Default: surrender vs. any card
    ):
        self.blackjack_pays = blackjack_pays
        self.decks = decks
        self.dealer_peeks_for_blackjack = dealer_peeks_for_blackjack
        self.dealer_hits_soft_17 = dealer_hits_soft_17
        self.double_allowed = double_allowed
        self.double_after_split = double_after_split
        self.split_2_to_10 = split_2_to_10
        self.split_aces = split_aces
        self.split_aces_draw = split_aces_draw
        self.surrender = surrender

    def __str__(self):
        return '|'.join([
            blackjack_payoffs[self.blackjack_pays],
            shoe_decks[self.decks],
            dealer_peek_options[self.dealer_peeks_for_blackjack],
            dealer_hit_options[self.dealer_hits_soft_17],
            double_options[self.double_allowed],
            double_after_split_options[self.double_after_split],
            split_2_to_10_options[self.split_2_to_10],
            split_aces_options[self.split_aces],
            split_aces_draw_options[self.split_aces_draw],
            surrender_options[self.surrender],
        ])
