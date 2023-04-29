import sys

from config import log_occasional
from deal import Deal


if __name__ == '__main__':
    cards = ''
    if len(sys.argv) > 1:
        cards = sys.argv[1]
    for tc in [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7]:
        deal = Deal.from_cards(cards=cards, true_count=tc)
        if deal.valuation_saved is None:
            deal.save(save_valuation=True)
    while True:
        log_occasional('All analysis complete! Turn off runner.', seconds=30)
