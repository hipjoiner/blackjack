"""
Compute exact expected values for Blackjack play
TO DO:
    Identify terminal deal state
    Define the output string that uniquely identifies terminal deal state
    Arrange to write terminal state out to file somewhere

"""
from rules import Rules
from table import Table


def main(hands):
    r = Rules(blackjack_pays=1.5)
    t = Table(rules=r)
    print(f'Rules: {t.rules}')
    for h in range(hands):
        t.clear()
        print(f'\nHand #{h + 1}:')
        t.deal_hand()


if __name__ == '__main__':
    deals = 1
    main(deals)
