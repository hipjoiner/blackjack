"""
Compute exact expected values for Blackjack play
"""
from table import Table
from rules import Rules


def main():
    r = Rules(blackjack_pays=1.5)
    t = Table(rules=r)
    t.show()
    deal = t.deal()
    deal.execute()
    print('')
    print(deal)


if __name__ == '__main__':
    main()
