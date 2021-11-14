"""
Parameters defining a complete bettor configuration:
    (All of them come from the rules of the table)
    Doubling options
    Double after split allowed
    Split 2 to 10 options
    Split aces options
    Split aces draw options
    Surrender options
"""
from player import Player
from strategy import Strategy


class Bettor(Player):
    def __init__(self, table, strategy_name):
        super().__init__(table, strategy_name)

    def __str__(self):
        return '_'.join([str(h) for h in self.hands])

    @property
    def done(self):
        if self._done:
            return True
        self._done = True
        if not self.hands:
            self._done = False
        for hand in self.hands:
            if not hand.done:
                self._done = False
        return self._done

    @done.setter
    def done(self, value):
        self._done = value

    @property
    def double(self):
        return self.table.rules.double_allowed

    @property
    def double_after_split(self):
        return self.table.rules.double_after_split

    @property
    def net(self):
        return sum([h.net for h in self.hands])

    @property
    def split_2_to_10(self):
        return self.table.rules.split_2_to_10

    @property
    def split_aces(self):
        return self.table.rules.split_aces

    @property
    def split_aces_draw(self):
        return self.table.rules.split_aces_draw

    @property
    def surrender(self):
        return self.table.rules.surrender

    def choose_play(self, hand):
        """This function governs all player choices about how to play each hand.
        Initially, we'll implement "optimal" non-counting play strategy.
        """
        """FIXME: Other "plays" include blackjack, bust, win, lose, push.
        These make the hand final, removing the need for subsequent dealer action.
        """
        if hand.num_cards < 2:
            return 'Draw'
        if hand.can_surrender and self.strategy.surrender(hand, self.dealer.up_card):
            return 'Surrender'
        if hand.can_split and self.strategy.split(hand, self.dealer.up_card):
            return 'Split'
        if hand.can_double and self.strategy.double(hand, self.dealer.up_card):
            return 'Double'
        if hand.can_hit and self.strategy.hit(hand, self.dealer.up_card):
            return 'Hit'
        return 'Stand'
