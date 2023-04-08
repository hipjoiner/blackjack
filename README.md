# Blackjack
Goal: compute exact expected values for Blackjack play

Hand play sequence

1. Bettor card 1
2. Dealer card up
3. Bettor card 2
4. Dealer card down
5. Bettor early surrender; if yes, hand is over
6. Bettor check for blackjack; if yes, hand is over
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

All actions
    Insurance   I
    Surrender   S
    Split       V
    Double      D
    Hit         H
    Stand       X

Table state representation
    Decks                           6D/8D/1D/2D/4D
    Dealer hit/stand soft 17        H17/S17
    Double after split allowed      DAS/NDS
    Double any two / 9-11 / 10-11   D2/D9/D10
    Split hands                     S0/S1/S2/S3
    Resplit Aces allowed            RSA/NRSA
    Surrender allowed               S/NS
e.g.,
    T 6D-S17-DAS-D2-S3-RSA-S

Player state representation
    Cards                           0-0-0-0-0-0-0-0-0-0     Ten-value array showing number of cards of each rank
    Insurance                       I/<empty>
    Surrender                       S/<empty>
    Split                           V<R>-<n>of<N>/<empty>    Rank R - hand n - total splits N
    Double                          D/<empty>
e.g.,
    P ^2-3-4-5-6-7-8-9-T-A
    P ^1-0-0-0-0-1-0-1-0-0
Player dealt 9 and 2, doubled, subsequently dealt a 7
OR
Player dealt 7 and 2, doubled, subsequently dealt a 9

Split representation
    Player-<hand-1-state>[|<hand-2-state>]...
    States sorted alphabetically

Dealer state representation
    Up card                         2/3/4/5/6/7/8/9/T/A
    Cards                           0-0-0-0-0-0-0-0-0-0     Ten-value array showing number of cards of each rank
e.g.,
    D 4^0-0-1-0-0-0-1-0-0-0

Full state representation
    <table state>-<dealer state>-<player state>
