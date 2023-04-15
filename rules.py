class Rules:
    def __init__(self, blackjack_pays, shoe_decks, hit_soft_17, double_allowed, splits_allowed, double_after_split, resplit_aces, late_surrender):
        self.blackjack_pays =  blackjack_pays
        self.shoe_decks = shoe_decks
        self.hit_soft_17 = hit_soft_17
        self.double_allowed = double_allowed
        self.splits_allowed = splits_allowed
        self.double_after_split = double_after_split
        self.resplit_aces = resplit_aces
        self.late_surrender = late_surrender

    @property
    def implied_name(self):
        rules = [
            'BJ',
            '3to2' if self.blackjack_pays == 1.5 else '6to5',
            f'{self.shoe_decks}D',
            'H17' if self.hit_soft_17 else 'S17',
            self.double_allowed,
            f'S{self.splits_allowed}',
            'DAS' if self.double_after_split else 'NDAS',
            'RSA' if self.resplit_aces else 'NRSA',
            'LS' if self.late_surrender else 'NS',
        ]
        return '-'.join(rules)

    @property
    def instreams(self):
        return (
            self.blackjack_pays,
            self.shoe_decks,
            self.hit_soft_17,
            self.double_allowed,
            self.splits_allowed,
            self.double_after_split,
            self.resplit_aces,
            self.late_surrender
        )
