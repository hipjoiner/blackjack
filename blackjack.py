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
    print(f'Iteration 0: {t}')
    d = Deal(t)
    i = 1
    while not d.terminal:
        d.run(1)
        print(f'Iteration {i}: {t}')
        i += 1


if __name__ == '__main__':
    main()
