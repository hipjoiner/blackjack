# Blackjack
Goal: compute exact expected values for Blackjack play


TO DO T 25Apr23:
* Continue work on summary output (to spreadsheet)
  * Add starting hand probabilities 
  * Find starting hands with sensitivity to action or count
* Figure out memory cleanup, to enable unattended runs
* Figure out computation & storage for shoes with altered counts

------------------------------------------------------------------------------------------------------------------------
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

------------------------------------------------------------------------------------------------------------------------
Table state
    Decks                           6D/8D/1D/2D/4D
    Dealer hit/stand soft 17        H17/S17
    Double after split allowed      DAS/NDS
    Double any two / 9-11 / 10-11   D2/D9/D10
    Split hands                     S0/S1/S2/S3
    Resplit Aces allowed            RSA/NRSA
    Surrender allowed               S/NS
e.g.
    BJ-6D-S17-DAS-D2-S3-RSA-S

------------------------------------------------------------------------------------------------------------------------
Player state representation
    Cards internal                  Ten-value array showing number of cards of each rank
    Cards for display               Sorted list (A first, T last)
    Surrendered                     R
    Split                           Vcxn        c is card of split; n is number of times split (typically 1-3)
    Double                          D
e.g.
    A35^D

------------------------------------------------------------------------------------------------------------------------
Dealer state representation
    Cards internal                  Ten-value array showing number of cards of each rank
    Cards for display               Sorted list, A first, T 2nd last, x for down card last
e.g.
    [9x]

------------------------------------------------------------------------------------------------------------------------
Full state representation
    <table state> <dealer state> <player state>
e.g.
    BJ-6D-S17-DAS-D2-S3-RSA-S [6x] 38^V8x2

