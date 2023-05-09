# Blackjack
Goal: compute exact expected values for Blackjack play


TO DO T 25Apr23:
* Summary output
  * Consolidate hard totals (e.g. 79 and 6T; 69 and 78 and 5T, etc.)
  * Go across TC runs to pull deviation output
* Clean up storage
  * Locate & delete states w/ fewer than N max nodes (e.g. 1,000,000)
* Cross TC run analysis
  * Construct EV line vs TC; find X-axis intersection: true count for EV-Zero
  * Do similar for all deviation plays: find true count for change in play for each hand


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
    <table state> <true count> <dealer state> <player state>
e.g.
    BJ-6D-S17-DAS-D2-S3-RSA-S TC+0 [6x] 38^V8x2

