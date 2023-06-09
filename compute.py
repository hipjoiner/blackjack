"""Run full computations for a variety of scenarios, saving results for summary w/ show_strategy.py
FIXME: Non-integer true counts
"""
from functools import cache

from config import log_occasional
from deal import Deal
from rules import Rules


@cache
def true_counts():
    counts = []
    for i in range(0, 6):
        for d in range(0, 10):
            tc = i + d / 10.0
            counts.append(tc)
            if tc != 0:
                counts.append(-tc)
    return counts


def rules_to_run():
    rules = []
    for hit_17 in [True, False]:
        for splits in [2]:
            for decks in [6, 4, 2]:
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
        for count in true_counts():
            deal = Deal(rules=rules.instreams, true_count=count)
            if deal.valuation_saved is None:
                deal.save(save_valuation=True)


if __name__ == '__main__':
    run_all_computations()
    while True:
        log_occasional('All analysis complete! Turn off runner.', seconds=300)
