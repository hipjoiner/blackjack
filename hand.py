"""
A hand should have all knowledge necessary to determine what options are available to it next:
    It should know if it's been split and how many times
    It should know if it's been doubled
    It should be able to know the dealer's up card so it can determine if Surrender is legal
        (Dealer's hand/up card should be an integral part of the hand)
    It won't know directly what options it has: it must ask the Rules to determine that.
"""
