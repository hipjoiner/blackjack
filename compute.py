"""Run full computations for a variety of scenarios, saving results for summary w/ show_strategy.py
FIXME: Non-integer true counts
"""
from config import log_occasional
from deal import Deal
from rules import Rules


true_counts = [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5]


def rules_to_run():
    rules = []
    for hit_17 in [True, False]:
        for splits in [3, 2]:
            for decks in [8, 4, 2]:
                rules.append(
                    Rules(
                        blackjack_pays=1.5,
                        shoe_decks=decks,
                        hit_soft_17=hit_17,
                        double_allowed='Any2',
                        splits_allowed=splits,
                        double_after_split=True,
                        resplit_aces=False,
                        late_surrender=True,
                    )
                )
    return rules


def run_all_computations():
    for rules in rules_to_run():
        for count in true_counts:
            deal = Deal(rules=rules.instreams, true_count=count)
            if deal.valuation_saved is None:
                deal.save(save_valuation=True)


if __name__ == '__main__':
    run_all_computations()
    while True:
        log_occasional('All analysis complete! Turn off runner.', seconds=300)
