"""
Compute exact expected values for Blackjack play
"""
from table import Table
from rules import Rules


def main():
    r = Rules(blackjack_pays=1.5)
    print(f'Rules: {r}')
    t = Table(rules=r)
    print(f'Table: {t}')
    print(f'Shoe: {t.shoe}')
    print(f'Dealer: {t.dealer}')
    print(f'Player: {t.player}')


if __name__ == '__main__':
    main()
