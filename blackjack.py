"""
Compute exact expected values for Blackjack play
"""
from deal import Deal
from rules import Rules
from table import Table


def main():
    r = Rules(blackjack_pays=1.5)
    t = Table(rules=r)
    print(f'Rules: {t.rules}')
    for h in range(1, 10):
        print(f'\nHand {h}:')
        d = Deal(t)
        while not d.terminal:
            if d.dealt:
                print(f'  {t}; ', end='')
            d.run(1)
        print(f'  Final: {t}')
        print(d)
        t.clear()


if __name__ == '__main__':
    main()
