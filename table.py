"""
Parameters defining a complete table configuration:
    Rules
        Table
            Blackjack pays:                 3-2, 7-5, 6-5, 1-1
            Shoe decks:                     1-8
        Dealer
            Dealer peeks for blackjack:     True/False
            Dealer hits soft 17:            True/False
        Player
            Doubling:                       any 2 cards, 9-11, 10-11, not allowed
            Split 2-10s:                    3 times, 2 times, 1 time, not allowed
            Split aces:                     3 times, 2 times, 1 time, not allowed
            Draw to split aces:             1 only, any
            Double after split:             True/False
            Surrender:                      any, any except ace, none
"""
from shoe import Shoe
from dealer import Dealer
from bettor import Bettor
from deal import Deal


class Table:
    def __init__(self, rules):
        self.rules = rules
        self.shoe = Shoe(rules.decks)
        self.dealer = Dealer(self)
        self.bettor = Bettor(self)
        self.deal = None

    def __str__(self):
        if self.deal is None:
            return 'Empty table'
        return str(self.deal)

    def clear(self):
        self.dealer.clear()
        self.bettor.clear()
        if self.shoe.depleted():
            print('\nShoe depleted; reshuffling...')
            self.shoe.shuffle()

    def deal_hand(self):
        self.deal = Deal(self)
        while not self.deal.done:
            if str(self.deal):
                print(f'{self.deal}; ', end='')
            play = self.deal.run()
            if play:
                print(play)
            self.deal.save()
        print(self.deal)
        print('Result: ' + '; '.join([f'{h.result} {h.net}' for h in self.bettor.hands]))
        print(f'Net: {self.bettor.net}')
