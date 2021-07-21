# Blackjack
Goal: compute exact expected values for Blackjack play

For any given deal state, compute all bettor's options (if any), and for each option,
compute expected return of entire deal.

For each state, we must determine
    Hand that is to play
    Available play options
    Notation for future states that could occur from play options

Data fully describing bettor's hand
    Cards in order
    Number of times split
    Surrendered?
    Doubled?
    Stood?

All actions; which ones must be explicit in notation?
    K   Peek                Yes, modifies hole card value
    R   Surrender           Yes, ends hand
    D   Double              Yes, ends hand
    S   Stand               Yes, ends hand
    C   Draw                No-- draw is part of rules; known
    T   Turn hole card      No-- evident by symbol
    P   Split               No-- evident by symbols
    H   Hit                 No-- evident by new card

Notation examples:

Identifier              State                               Next state
----------------------  ----------------------------------  ---------------------------
Deal--                  Table clear, no cards yet           Bettor draw
Deal--8                 Bettor dealt an 8                   Dealer draw
Deal-A-8                Dealer dealt an A                   Bettor draw
Deal-A-88               Bettor dealt an 8                   Dealer draw

Deal-Ax-88              Dealer dealt hole card              If peek for blackjack, dealer peeks
                                                            If no peek, bettor play

Deal-AT-88              Dealer peeks, has blackjack         None

Deal-AxK-88             Dealer peeks (K), no blackjack      Bettor play

Deal-AxK-88R            Bettor surrenders (R)               None

Deal-AxK-8-8            Bettor splits                       Bettor draw, hand 1
Deal-AxK-8T-8           Bettor draws a T to hand 1          Bettor option, hand 1
Deal-AxK-8TS-8          Bettor hand 1 stands (S)            Bettor draw, hand 2
Deal-AxK-8TS-83         Bettor hand 2 dealt a 3             Bettor option, hand 2

Deal-AxK-8TS-837D       Bettor hand 2 doubles, draws a 7    Dealer reveal
Deal-A7K-8TS-837D       Dealer reveals 7                    Dealer play
Deal-A7KS-8TS-837D      Dealer stands (S)                   None






