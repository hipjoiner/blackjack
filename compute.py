import sys

from deal import Deal


if __name__ == '__main__':
    cards = ''
    if len(sys.argv) > 1:
        cards = sys.argv[1]
    deal = Deal.from_cards(cards=cards)
    deal.save(save_valuation=True)
