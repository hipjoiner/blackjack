"""
A complete player strategy must answer 4 questions for any hand and dealer up card:
    Should I surrender?
    Should I split?
    Should I double?
    Should I hit?
"""


class Strategy:
    """Below is basic (non-counting) optimal strategy.
        https://www.blackjackapprenticeship.com/blackjack-strategy-charts/
    """
    @staticmethod
    def surrender(hand, dlr_up):
        if hand.total == 16 and dlr_up in ['9', 'T', 'A']:
            return True
        if hand.total == 15 and dlr_up == 'T':
            return True
        return False

    @staticmethod
    def split(hand, dlr_up):
        lookup = {
            'AA': lambda d: True,
            'TT': lambda d: False,
            '99': lambda d: d in ['2', '3', '4', '5', '6', '8', '9'],
            '88': lambda d: True,
            '77': lambda d: d in ['2', '3', '4', '5', '6', '7'],
            '66': lambda d: d in ['2', '3', '4', '5', '6'],
            '55': lambda d: False,
            '44': lambda d: d in ['5', '6'],
            '33': lambda d: d in ['2', '3', '4', '5', '6', '7'],
            '22': lambda d: d in ['2', '3', '4', '5', '6', '7'],
        }
        return lookup[hand.cards](dlr_up)

    @staticmethod
    def double(hand, dlr_up):
        if hand.soft:
            lookup = {
                19: lambda d: d in ['6'],
                18: lambda d: d in ['2', '3', '4', '5', '6'],
                17: lambda d: d in ['3', '4', '5', '6'],
                16: lambda d: d in ['4', '5', '6'],
                15: lambda d: d in ['4', '5', '6'],
                14: lambda d: d in ['5', '6'],
                13: lambda d: d in ['5', '6'],
            }
        else:
            lookup = {
                11: lambda d: True,
                10: lambda d: d in ['2', '3', '4', '5', '6', '7', '8', '9'],
                9: lambda d: d in ['3', '4', '5', '6'],
            }
        return lookup.get(hand.total, lambda d: False)(dlr_up)

    @staticmethod
    def hit(hand, dlr_up):
        if hand.soft:
            if hand.total == 18 and dlr_up in ['9', 'T', 'A']:
                return True
            return hand.total <= 17
        if hand.total >= 17:
            return False
        if hand.total <= 11:
            return True
        lookup = {
            16: lambda d: d in ['7', '8', '9', 'T', 'A'],
            15: lambda d: d in ['7', '8', '9', 'T', 'A'],
            14: lambda d: d in ['7', '8', '9', 'T', 'A'],
            13: lambda d: d in ['7', '8', '9', 'T', 'A'],
            12: lambda d: d in ['2', '3', '7', '8', '9', 'T', 'A'],
        }
        return lookup.get(hand.total, lambda d: False)(dlr_up)
