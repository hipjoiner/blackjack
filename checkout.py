from datetime import datetime
import os
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
        '20':  ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'],
        '19':  ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'],
        '18':  ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'],
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
        '7':   ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
        '6':   ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
        '5':   ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'],
    },
    'Surrender': {
        'Dlr': ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'A'],
        '17':  ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'Y'],
        '16':  ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'Y', 'Y', 'Y'],
        '15':  ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'Y', 'Y'],
    },
}


play_codes = {
    'i': 'Insurance',
    'l': 'Surrender',
    'v': 'Split',
    'd': 'Double',
    'h': 'Hit',
    's': 'Stand',
}


def ask_and_answer(q, correct, num):
    print(f'\n({num:03}) {q:20}', end='', flush=True)
    resp = ''
    while True:
        key = readkey()
        print(key, end='', flush=True)
        resp += key.lower()
        if is_query(resp) or is_correct(resp, correct) or is_wrong(resp, correct):
            return resp


def create_exercises():
    strategy_cases = {}
    for hand_type, hands in strategy.items():
        dealer_cards = hands.pop('Dlr')
        for hand_case, plays in hands.items():
            hand = get_representative_hand(hand_type, hand_case)
            hand_cards = ', '.join(list(hand.cards))
            for i, play in enumerate(plays):
               dealer_card = dealer_cards[i]
               key = f'{hand_case:3} vs {dealer_card}'
               data = {
                   'q': f'{hand_cards} vs {dealer_card}',
                   'a': get_play_code(hand, hand_case, i),
                   'hand': hand,
               }
               strategy_cases[key] = data

    exercises = {}
    for case, data in strategy_cases.items():
        exercises[case] = data
        exercises[case]['responses'] = []
        exercises[case]['elapsed'] = 0
    return exercises


def get_permutations_recursive(total):
    """Return all integer value permutations for cards for a hard total hand"""
    if total == 1:
        return [1]
    perms = set()
    for i in range(1, int((total + 1) / 2)):
        sub_perms = get_permutations_recursive(total - i)
        for sub_perm in sub_perms:
            perms.add(sub_perm + (1,))
    if total <= 10:
        perms.add((total,))
    return perms


def get_rep_hard_total(total):
    """Choose a permutation of digits adding up to a given total, with these restrictions:
        Must be at least 2 values
        Can't be a pair
        Can't be a soft total (i.e., numbers total between 1 and 11 and contains a 1)
        Can't be a surrenderable hand (two cards adding up to 15, 16 or 17)
    So construct all permutations, any number of cards, and then eliminate the above if start is True.
    """
    perms = get_permutations_recursive(total)
    ok_perms = perms
    rep = random.choice(perms)
    return rep


def get_representative_cards(hand_type, hand_case):
    """FIXME: Do this better, with variety of cards, unsorted"""
    if hand_type in ['Pair', 'Soft']:
        return hand_case.split(',')
    if hand_type == 'Surrender':
        reps = {
            '17': ['7T', '89'],
            '16': ['6T', '79'],
            '15': ['5T', '69', '78'],
        }
        return list(random.choice(reps[hand_type]))
    """Hard totals. Can't be pairs, or soft, or an otherwise surrenderable of only 2 cards."""
    total = int(float(hand_case))
    cards = get_rep_hard_total(total)
    return cards


def get_representative_hand(hand_type, hand_case):
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
    representative_cards = get_representative_cards(hand_type, hand_case)
    for card in representative_cards:
        hand = hand.new_hand(card)
    return hand


def get_play_code(hand, hand_case, dealer_card_index):
    if hand.can_surrender and not hand.is_soft and not hand.is_pair:
        play = strategy['Surrender'].get(str(hand.total), [''] * 10)[dealer_card_index]
        if play == 'Y':
            return 'l'
    if hand.is_pair:
        play = strategy['Pair'][hand_case][dealer_card_index]
        if play == 'Y':
            return 'v'
    if hand.is_soft:
        play = strategy['Soft'][hand_case][dealer_card_index]
        if play.startswith('D'):
            if hand.can_double:
                return 'd'
            return play[1]
        return play.lower()
    play = strategy['Hard'].get(str(hand.total), [''] * 10)[dealer_card_index]
    if play.startswith('D'):
        if hand.can_double:
            return 'd'
        return play[1]
    if play == '':
        if hand.total > 17:
            return 's'
        return 'h'
    return play.lower()


def get_play_from_code(play_code):
    """FIXME: Do this for deviations as well"""
    return play_codes[play_code]


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


def report_results(exercises):
    results = []
    tot_questions = 0
    tot_wrong = 0
    tot_elapsed = 0
    for q, data in exercises.items():
        a = data['a']
        correct, totq = get_record(data['responses'])
        wrong = totq - correct
        e = data['elapsed']
        if totq == 0:
            continue
        results.append({
            'q': q,
            'a': a,
            'correct': correct,
            'wrong': wrong,
            'tot': totq,
            'pct': correct / totq,
            'time': e,
            'key': f'{totq - correct:02d}|{e:02.2f}'
        })
        # print(f'{q:10} ({a}): {correct:3} of {tot:3}')
        tot_questions += totq
        tot_wrong += wrong
        tot_elapsed += e
    print(f'\nResults:\n')
    results = sorted(results, key=lambda d: d['key'], reverse=True)
    for r in results[:10]:
        print(f"{r['q']} ({get_play_from_code(r['a']):9}): {r['wrong']} wrong, {r['time']:.2f} sec")
    tot_pct = (tot_questions - tot_wrong) / tot_questions
    print()
    print(f'Results: {tot_questions - tot_wrong}/{tot_questions} right, {tot_wrong} wrong ({tot_pct:.1%})')
    print(f'Elapsed: {tot_elapsed:.0f} sec ({tot_elapsed / tot_questions:.2f} sec per question)')


def drill():
    exercises = create_exercises()
    qs = list(exercises.keys())
    tot_ex = len(qs)
    try:
        # Keep asking questions until user quits or we ask all
        remaining = len(qs)
        while remaining:
            os.system('cls')
            i = random.randint(0, len(qs) - 1)
            hand_case = qs.pop(i)
            q = exercises[hand_case]['q']
            a = exercises[hand_case]['a']
            remaining = len(qs)
            # Keep asking this particular question until user gets it right
            correct = False
            while not correct:
                start_time = datetime.now()
                response = ask_and_answer(q, a, tot_ex - remaining)
                elapsed = datetime.now() - start_time
                exercises[hand_case]['elapsed'] += elapsed.total_seconds()
                if is_query(response):
                    exercises[hand_case]['responses'].append('Ask')
                    print(f'        {hand_case}: {get_play_from_code(a)}')
                elif is_wrong(response, a):
                    exercises[hand_case]['responses'].append('Wrong')
                    print(f'        WRONG: {hand_case} = {get_play_from_code(a)}')
                else:
                    exercises[hand_case]['responses'].append('Correct')
                    print(f'        Correct')
                    correct = True
    except KeyboardInterrupt:
        pass
    os.system('cls')
    report_results(exercises)


if __name__ == '__main__':
    drill()
