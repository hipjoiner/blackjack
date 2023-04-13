from config import home_dir


class Rules:
    """
    Blackjack                       B32/B65
    Decks                           6D/8D/1D/2D/4D
    Dealer hit/stand soft 17        H17/S17
    Double after split allowed      DAS/NDS
    Double any two / 9-11 / 10-11   D2/D9/D10
    Split hands                     S0/S1/S2/S3
    Resplit Aces allowed            RSA/NRSA
    Surrender allowed               LS/NS

    R 6D-S17-DAS-D2-S3-RSA-S
    """

    def __init__(self, blackjack='B32', decks=6, soft_17='S17', das='DAS', double_any='D2', splits='S3', rsa='RSA', surrender='S'):
        self.blackjack = blackjack
        self.decks = decks
        self.soft_17 = soft_17
        self.das = das
        self.double_any = double_any
        self.splits = splits
        self.rsa = rsa
        self.surrender = surrender

    def __repr__(self):
        return self.name

    @property
    def state(self):
        return {
            'spec': self.name,
            'decks': self.decks,
            'soft_17': self.soft_17,
            'double_after_split': self.das,
            'double_any': self.double_any,
            'split_hands': self.splits,
            'resplit_aces': self.rsa,
            'late_surrender': self.surrender,
        }

    @property
    def fpath(self):
        return f'{home_dir}/rules/{self.name}.json'

    @property
    def name(self):
        return f'R {self.decks}D-{self.soft_17}-{self.das}-{self.double_any}-{self.splits}-{self.rsa}-{self.surrender}'


if __name__ == '__main__':
    r = Rules()
    print(r.state)
