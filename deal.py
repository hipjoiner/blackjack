"""
A deal is a fully dealt round of cards, all options exhausted, all hands final, wins and losses determined.
A deal incorporates both player activity and dealer activity.
This is the focus for computation of expected value.
The deal will start with a single player hand, but may split into two or more hands.
We compute expected value for each of the splits of course, since we are computing recursively,
but the deal EV is the one of primary interest to us.
"""
from hand import Hand


class Deal:
    def __init__(self, table, dhand=None, phands=None):
        self.table = table
        if dhand is None:
            dhand = Hand(self.table.dealer)
        self.dhand = dhand
        if phands is None:
            phands = [Hand(self.table.player)]
        self.phands = phands

    def __str__(self):
        s = f'D-{self.dhand}'
        for i, hand in enumerate(self.phands):
            s += f'|P{i}-{hand}'
        return s

    def execute(self):
        print('Executing...')
        self.dhand.draw()
        self.phands[0].draw()
        self.dhand.draw()
        self.phands[0].draw()
