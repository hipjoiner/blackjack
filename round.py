"""
A play is a full dealt round of cards, with all options exhausted, all hands final and wins and losses determined.
A play incorporates both player activity and dealer activity.
This is the focus for computation of expected value.
The play will start a deal with a single hand, but may split into two or more hands.
We will compute expected value for each of the splits of course, since we are computing recursively,
but the play EV is the one of primary interest to us.
"""
