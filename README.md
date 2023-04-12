# Blackjack
Goal: compute exact expected values for Blackjack play

Hand play sequence

1. Bettor card 1
2. Dealer card up
3. Bettor card 2
4. Dealer card down
5. Insurance offer
6. Insurance acceptance
7. Dealer check for blackjack; if yes, hand is over
8. Bettor surrender; if yes, hand is over
9. Bettor play option
10. Bettor all busted; if yes, hand is over
11. Dealer play option
12. Hand is over
13. Evaluate win/loss

For any given deal state, the only important question is: is it terminal?
Are no more cards needed?
If true, compute EV.
If not, construct subsequent states.

Actions
    Insurance   I
    Surrender   S
    Split       V
    Double      D
    Hit         H
    Stand       X


------------------------------------------------------------------------------------------------------------------------
Table state
    Decks                           6D/8D/1D/2D/4D
    Dealer hit/stand soft 17        H17/S17
    Double after split allowed      DAS/NDS
    Double any two / 9-11 / 10-11   D2/D9/D10
    Split hands                     S0/S1/S2/S3
    Resplit Aces allowed            RSA/NRSA
    Surrender allowed               S/NS

    T 6D-S17-DAS-D2-S3-RSA-S


------------------------------------------------------------------------------------------------------------------------
Player state representation
                                    2-3-4-5-6-7-8-9-T-A
    Cards                           0-0-0-0-0-0-0-0-0-0     Ten-value array showing number of cards of each rank
    Insurance taken                 I                       Insurance, surrender and split modify the overall round
    Surrendered                     R
    Split                           Sn

    Double                          D                       Double modifies each individual (possibly split) hand


    P D^1-0-0-0-0-1-0-1-0-0

Player dealt 9 and 2, doubled, subsequently dealt a 7
OR
Player dealt 7 and 2, doubled, subsequently dealt a 9

Split representation
    P <hand-1-state> [<hand-2-state>]...
    Sort hand states alphabetically to reduce number of permutations

    P S2 D^1-0-0-0-0-1-0-1-0-0 ^1-0-0-1-0-0-0-0-1-0

Dealt pair of 2s; split. First hand dealt 9 (or 7), doubled, got 7 (or 9). Second hand dealt 5 and T (order unknown).


------------------------------------------------------------------------------------------------------------------------
Dealer state representation
    Up card                         2/3/4/5/6/7/8/9/T/A
    Cards                           0-0-0-0-0-0-0-0-0-0     Ten-value array showing number of cards of each rank
    Insurance offered               I

    D 4^1-0-0-0-0-0-1-0-0-0
    D I A^0-0-0-0-0-0-0-0-1-1


------------------------------------------------------------------------------------------------------------------------
Full state representation
    <table state> # <dealer state> # <player state>

    T 6D-S17-DAS-D2-S3-RSA-S # D 4^1-0-0-0-0-0-1-0-0-0 # P S2 D^1-0-0-0-0-1-0-1-0-0 ^1-0-0-1-0-0-0-0-1-0

