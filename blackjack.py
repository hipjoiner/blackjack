"""
Compute exact expected values for Blackjack play
TO DO:
    Identify terminal deal state
    Define the output string that uniquely identifies terminal deal state
    Arrange to write terminal state out to file somewhere

"""
import sys

from table import Table


def main(hands):
    t = Table('Table1')
    for h in range(hands):
        t.clear()
        print(f'\nHand #{h + 1}:')
        t.deal_hand()


if __name__ == '__main__':
    print(f'Argv:\n{sys.argv}')
    deals = 1
    main(deals)
