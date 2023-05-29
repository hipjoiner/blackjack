from datetime import datetime
from functools import cache
import random
from readchar import readkey

from rules import Rules
from deal import Deal
from hand import Hand


strategy = {
    'Pair': {
        'Dlr': ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A'],
        'A,A': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
        'T,T': ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        '9,9': ['Y', 'Y', 'Y', 'Y', 'Y', 'N', 'Y', 'Y', 'N', 'N'],
        '8,8': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
        '7,7': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'N', 'N', 'N', 'N'],
        '6,6': ['Y', 'Y', 'Y', 'Y', 'Y', 'N', 'N', 'N', 'N', 'N'],
        '5,5': ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        '4,4': ['N', 'N', 'N', 'Y', 'Y', 'N', 'N', 'N', 'N', 'N'],
        '3,3': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'N', 'N', 'N', 'N'],
        '2,2': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'N', 'N', 'N', 'N'],
    },
    'Soft': {
        'Dlr': ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A'],
        'A,9': ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'],
        'A,8': ['S', 'S', 'S', 'S', 'Ds', 'S', 'S', 'S', 'S', 'S'],
        'A,7': ['Ds', 'Ds', 'Ds', 'Ds', 'Ds', 'S', 'S', 'H', 'H', 'H'],
        'A,6': ['H', 'Dh', 'Dh', 'Dh', 'Dh', 'H', 'H', 'H', 'H', 'H'],
        'A,5': ['H', 'H', 'Dh', 'Dh', 'Dh', 'H', 'H', 'H', 'H', 'H'],
        'A,4': ['H', 'H', 'Dh', 'Dh', 'Dh', 'H', 'H', 'H', 'H', 'H'],
        'A,3': ['H', 'H', 'H', 'Dh', 'Dh', 'H', 'H', 'H', 'H', 'H'],
        'A,2': ['H', 'H', 'H', 'Dh', 'Dh', 'H', 'H', 'H', 'H', 'H'],
    },
    'Hard': {
        'Dlr': ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A'],
        '17':  ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'],
        '16':  ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
        '15':  ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
        '14':  ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
        '13':  ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
        '12':  ['H', 'H', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
        '11':  ['Dh', 'Dh', 'Dh', 'Dh', 'Dh', 'Dh', 'Dh', 'Dh', 'Dh', 'Dh'],
        '10':  ['Dh', 'Dh', 'Dh', 'Dh', 'Dh', 'Dh', 'Dh', 'Dh', 'H', 'H'],
        '9':   ['H', 'Dh', 'Dh', 'Dh', 'Dh', 'H', 'H', 'H', 'H', 'H'],
        '8':   ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
    },
    'Surrender': {
        'Dlr': ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A'],
        '17':  ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'Y'],
        '16':  ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'Y', 'Y', 'Y'],
        '15':  ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'Y', 'Y'],
    },
}


tests = {
    'Pair': {
        'A,A': ['A', 'A'],
        'T,T': ['T', 'T'],
        '9,9': ['9', '9'],
        '8,8': ['8', '8'],
        '7,7': ['7', '7'],
        '6,6': ['6', '6'],
        '5,5': ['5', '5'],
        '4,4': ['4', '4'],
        '3,3': ['3', '3'],
        '2,2': ['2', '2'],
    },
    'Soft': {
        'A,9': ['A', '9'],
        'A,8': ['A', '8'],
        'A,7': ['A', '7'],
        'A,6': ['A', '6'],
        'A,5': ['A', '5'],
        'A,4': ['A', '4'],
        'A,3': ['A', '3'],
        'A,2': ['A', '2'],
    },
    'Hard': {
        '18': ['8', '7', '3'],
        '17': ['9', '5', '3'],
        '16': ['T', '2', '4'],
        '15': ['4', '6', '5'],
        '14': ['4', '2', '8'],
        '13': ['8', '5'],
        '12': ['9', '3'],
        '11': ['6', '5'],
        '10': ['7', '3'],
        '9': ['5', '4'],
        '8': ['6', '2'],
    },
    'Surrender': {
        '17': ['T', '7'],
        '16': ['T', '6'],
        '15': ['8', '7'],
    },
}


def ask_and_answer(q, correct, num):
    # os.system('cls')
    print(f'(#{num:3}) {q:20}', end='', flush=True)
    resp = ''
    while True:
        key = readkey()
        print(key, end='', flush=True)
        resp += key.lower()
        if is_query(resp) or is_correct(resp, correct) or is_wrong(resp, correct):
            return resp


@cache
def create_exercises():
    exercises = {}
    for hand_type, hands in strategy.items():
        dlr_cds = hands.pop('Dlr')
        for hand_str, plays in hands.items():
            for i, play in enumerate(plays):
               dlr_cd = dlr_cds[i]
               q = f'{hand_str:3} vs {dlr_cd}'
               data = {
                   'a': play_code(hand_type, hand_str, i),
                   'responses': [],
                   'elapsed': 0,
               }
               exercises[q] = data
    return exercises


def get_hand(hand_type, hand_str):
    decks = 8
    rules = Rules(
        blackjack_pays=1.5,
        shoe_decks=decks,
        hit_soft_17=True,
        double_allowed='Any2',
        splits_allowed=3,
        double_after_split=True,
        resplit_aces=False,
        late_surrender=True,
    )
    deal = Deal(rules=rules.instreams)
    hand = Hand(deal=deal, player='Player')
    test = tests[hand_type][hand_str]
    for card in test:
        hand = hand.new_hand(card)
    return hand


def get_record(responses):
    tot = len(responses)
    correct = sum([1 if resp == 'Correct' else 0 for resp in responses])
    return correct, tot


def is_query(resp):
    return 'q' in resp


def is_correct(resp, correct):
    return resp == correct


def is_wrong(resp, correct):
    return not correct.startswith(resp)


def play_code(hand_type, hand_str, dlr_cd_i):
    h = get_hand(hand_type, hand_str)
    if h.can_surrender and not h.is_soft and not h.is_pair:
        play = strategy['Surrender'].get(str(h.total), [''] * 10)[dlr_cd_i]
        if play == 'Y':
            return 'l'
    if h.is_pair:
        play = strategy['Pair'][hand_str][dlr_cd_i]
        if play == 'Y':
            return 'v'
    if h.is_soft:
        play = strategy['Soft'][hand_str][dlr_cd_i]
        if play.startswith('D'):
            if h.can_double:
                return 'd'
            return play[1]
        return play.lower()
    play = strategy['Hard'].get(str(h.total), [''] * 10)[dlr_cd_i]
    if play.startswith('D'):
        if h.can_double:
            return 'd'
        return play[1]
    if play == '':
        if h.total > 17:
            return 's'
        return 'h'
    return play.lower()


def report_results(exercises):
    results = []
    all_tot = 0
    for q, data in exercises.items():
        a = data['a']
        correct, tot = get_record(data['responses'])
        e = data['elapsed']
        if tot == 0:
            continue
        results.append({
            'q': q,
            'a': a,
            'correct': correct,
            'tot': tot,
            'pct': correct / tot,
            'time': e,
        })
        # print(f'{q:10} ({a}): {correct:3} of {tot:3}')
        all_tot += tot
    print(f'\n\nResults, {all_tot} questions:')
    results = sorted(results, key=lambda d: d['pct'])
    for r in results[:10]:
        print(f"{r['q']} ({r['a']}): {r['pct']:.0%} in {r['time']:.2f}s")


def drill():
    exercises = create_exercises()
    qs = list(exercises.keys())
    tot_ex = len(qs)
    try:
        # Keep asking questions until user quits
        remaining = len(qs)
        while remaining:
            i = random.randint(0, len(qs) - 1)
            q = qs.pop(i)
            remaining = len(qs)
            a = exercises[q]['a']
            # Keep asking this particular question until user gets it right
            while True:
                start_time = datetime.now()
                response = ask_and_answer(q, a, tot_ex - remaining)
                elapsed = datetime.now() - start_time
                exercises[q]['elapsed'] += elapsed.total_seconds()
                if is_query(response):
                    exercises[q]['responses'].append('Ask')
                    print(f'        {q}: {a}')
                elif is_wrong(response, a):
                    exercises[q]['responses'].append('Wrong')
                    print(f'        WRONG: {q} = {a}')
                else:
                    exercises[q]['responses'].append('Correct')
                    print(f'        Correct')
                    break
    except KeyboardInterrupt:
        pass
    report_results(exercises)


if __name__ == '__main__':
    drill()
