import json
import os

from config import CachedInstance, home_dir, log
from hand import Hand
from rules import Rules
from shoe import Shoe


class Deal(metaclass=CachedInstance):
    saves = 0

    def __init__(
        self,
        rules=(1.5, 6, False, 'Any2', 3, True, True, True),
        dealer_hand=((0, 0, 0, 0, 0, 0, 0, 0, 0, 0), False, False, False),
        player_hands=(((0, 0, 0, 0, 0, 0, 0, 0, 0, 0), False, False, False),)
    ):
        self.rules = Rules(*rules)
        self.shoe = Shoe(self)
        self.dealer = Hand(self, 'D', *dealer_hand)
        self.player = [Hand(self, 'P', *ph) for ph in player_hands]
        self.saves = 0
        log(f'{self.implied_name}...')

    def __repr__(self):
        return self.implied_name

    @property
    def fpath(self):
        p = f'{home_dir}/states/{self.implied_name}.json'
        return p

    @staticmethod
    def from_cards(cards):
        """Instantiate a Deal state using the cards supplied as if dealt in order."""
        d = Deal()
        for c in cards:
            d = d.new_deal(c)
        return d

    @property
    def implied_name(self):
        return f'{self.rules.implied_name} {str(self.dealer)} {" ".join(str(h) for h in self.player)}'

    @property
    def is_terminal(self):
        return self.next_hand is None

    def load(self):
        if not os.path.isfile(self.fpath):
            return None
        with open(self.fpath, 'r') as fp:
            contents = json.load(fp)
        return contents['deal']

    def new_deal(self, card='', surrendered=None, doubled=None, stand=None):
        dealer_hand = self.dealer
        player_hands = self.player.copy()
        index = self.next_hand_index
        old_hand = self.next_hand
        sur = old_hand.surrendered
        if surrendered is not None:
            sur = surrendered
        dbl = old_hand.doubled
        if doubled is not None:
            dbl = doubled
        std = old_hand.stand
        if stand is not None:
            std = stand
        new_hand = self.next_hand.new_hand(card=card, surrendered=sur, doubled=dbl, stand=std)
        if index is None:
            dealer_hand = new_hand
        else:
            player_hands[index] = new_hand
        return Deal(
            rules=self.rules.instreams,
            dealer_hand=dealer_hand.instreams,
            player_hands=tuple(ph.instreams for ph in player_hands)
        )

    @property
    def next_hand(self):
        # Deal phase
        if self.player[0].num_cards == 0:
            return self.player[0]
        if self.dealer.num_cards == 0:
            return self.dealer
        if self.player[0].num_cards == 1:
            return self.player[0]
        if self.dealer.num_cards == 1:
            return self.dealer

        # Check for Blackjacks phase
        if self.dealer.is_blackjack:
            return None
        if self.player[0].is_blackjack:
            return None

        # If player all busted, dealer doesn't play
        player_all_busted = True
        for h in self.player:
            if not h.is_busted and not h.surrendered:
                player_all_busted = False
        if player_all_busted:
            return None

        for h in self.player:
            if not h.is_terminal:
                return h
        if not self.dealer.is_terminal:
            return self.dealer
        return None

    @property
    def next_hand_index(self):
        h = self.next_hand
        if h == self.dealer:
            return None
        for i, ph in enumerate(self.player):
            if h == ph:
                return i
        return None

    @property
    def next_hand_actions(self):
        if self.next_hand is None:
            return None
        return self.next_hand.actions

    @property
    def next_states(self):
        if self.next_hand_actions is None:
            return None
        states = {}
        for action in self.next_hand_actions:
            if action == 'Deal':
                states['Deal'] = self.next_states_add_card()
            elif action == 'Surrender':
                # A Surrender gets no new card, just a new state
                states['Surrender'] = {
                    'calcs': {
                        'nodes': 1,
                        'value': -0.5,
                    }
                }
            elif action == 'Split':
                states['Split'] = {}
            elif action == 'Double':
                states['Double'] = self.next_states_add_card(doubled=True)
            elif action == 'Hit':
                states['Hit'] = self.next_states_add_card()
            elif action == 'Stand':
                new_deal = self.new_deal(stand=True)
                states['Stand'] = {
                    'calcs': {
                        'nodes': None,
                        'value': None,
                    },
                    'children': {
                        '': {
                            'state': new_deal.implied_name,
                            'prob': 1.0,
                        } | new_deal.state_calcs
                    }
                }
        for action, data in states.items():
            if 'children' in states[action]:
                states[action]['calcs'] = self.next_states_calcs(states[action]['children'])
        return states

    def next_states_add_card(self, doubled=None):
        # A Deal action gets a new card, so we enumerate states by new card.
        children = {}
        for card, prob in self.shoe.pdf.items():
            new_deal = self.new_deal(card, doubled=doubled)
            new_deal.save()
            Deal.saves += 1
            children[card] = {
                'state': new_deal.implied_name,
                'prob': prob,
            }
            # for key, val in new_deal.state_calcs.items():
            #     children[card][key] = val
            children[card] = children[card] | new_deal.state_calcs
        result = {
            'children': children
        }
        return result

    def next_states_calcs(self, children):
        # Iterate through the child states to see if we have terminal/summary info on all, in which case we summarize at this level.
        nodes = 0
        value = 0
        for card, data in children.items():
            if not data['terminal']:
                nodes = None
                value = None
                break
            nodes += data['nodes']
            value += data['prob'] * data['value']
        result = {
            'nodes': nodes,
            'value': value,
        }
        return result


    def save(self):
        log(f'Saving {self.fpath}...')
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
        s = self.state      # Computing this may involve loading it, which we must do before we open the file to write
        with open(self.fpath, 'w') as fp:
            json.dump(s, fp, indent=4)

    @property
    def splits(self):
        return len(self.player) - 1

    @property
    def state(self):
        return {
            'state': self.implied_name,
            'calcs': self.state_calcs,
            'player': [h.state for h in self.player],
            'dealer': self.dealer.state,
            'rules': self.rules.implied_name,
            'shoe': {
                'cards': self.shoe.cards,
                'pdf': self.shoe.pdf,
            },
        }

    @property
    def state_calcs(self):
        if os.path.isfile(self.fpath):
            log(f'Loading {self.fpath}...')
            with open(self.fpath, 'r') as fp:
                data = json.load(fp)
            calcs = data['calcs']
            calcs['loaded'] = True
        else:
            if self.next_hand == self.dealer:
                to_play = 'Dealer'
            elif self.next_hand is None:
                to_play = None
            else:
                to_play = 'Player'
            calcs = {
                'terminal': self.is_terminal,
                'nodes': 1 if self.is_terminal else None,
                'loaded': False,
            }
            if self.is_terminal:
                calcs['value'] = self.value
            else:
                calcs['hand_to_play'] = to_play
                calcs['hand_index'] = self.next_hand_index
                calcs['actions'] = self.next_states
        return calcs

    @property
    def value(self):
        if not self.is_terminal:
            return None
        val = 0
        for h in self.player:
            val += h.value
        return val


if __name__ == '__main__':
    deal = Deal.from_cards('A58')
    deal.save()
