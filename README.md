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
If not, construct subsequent states by adding 1 more card.

All actions
    Deal
    Surrender
    Peek
    Reveal
    Split
    Double
    Hit
    Stand

Notation
    <table>-<card sequence>
    Table1-A75T

Given a table config and card sequence
    Allocate each card to bettor or dealer as appropriate
    Ask player to show hand configuration & details given card sequence received

