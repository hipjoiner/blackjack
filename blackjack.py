"""
Compute exact expected values for Blackjack play
TO DO:
    Identify terminal deal state
    Define the output string that uniquely identifies terminal deal state
    Arrange to write terminal state out to file somewhere

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
            d.run()
        print(f'  {d}')
        t.clear()


if __name__ == '__main__':
    main()
