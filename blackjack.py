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
    d = Deal(t)
    i = 1
    while not d.terminal:
        print(f'Step {i}: {t}; ', end='')
        d.run(1)
        i += 1
    print(f'Final: {t}')


if __name__ == '__main__':
    main()
