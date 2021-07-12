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


def main(hands):
    r = Rules(blackjack_pays=1.5)
    t = Table(rules=r)
    print(f'Rules: {t.rules}')
    for h in range(hands):
        print(f'\nHand {h + 1}:')
        d = Deal(t)
        d.save()
        while not d.done:
            if d.dealt:
                print(f'  {d}  {t}; {d.cards}; ', end='')
            d.run()
            d.save()
        print(f'  {d}  {t}; {d.cards}')
        # d.save()
        print('  Result: ' + '; '.join([f'{h.outcome}, {h.net:+.1f}' for h in d.bettor.hands]))
        t.clear()


if __name__ == '__main__':
    deals = 3
    main(deals)
