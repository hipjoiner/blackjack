from config import log_occasional
from deal import Deal
from rules import Rules


true_counts_to_run = [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 10, -10]


def run_all_computations():
    rules = Rules(
        blackjack_pays=1.5,
        shoe_decks=8,
        hit_soft_17=True,
        double_allowed='Any2',
        splits_allowed=3,
        double_after_split=True,
        resplit_aces=False,
        late_surrender=True,
    )
    for tc in true_counts_to_run:
        deal = Deal(rules=rules.instreams, true_count=tc)
        if deal.valuation_saved is None:
            deal.save(save_valuation=True)


if __name__ == '__main__':
    run_all_computations()
    while True:
        log_occasional('All analysis complete! Turn off runner.', seconds=30)
