from functools import cached_property
import json
import os

from config import CachedInstance, home_dir, log
from hand import Hand
from rules import Rules
from shoe import Shoe


class Deal(metaclass=CachedInstance):
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
        log(f'{self.implied_name}...')

    def __repr__(self):
        return self.implied_name

    @property
    def fpath(self):
        return f'{home_dir}/states/{self.implied_name}.json'

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
    def is_done(self):
        return self.next_hand is None

    def load(self):
        if not os.path.isfile(self.fpath):
            return None
        with open(self.fpath, 'r') as fp:
            contents = json.load(fp)
        return contents['deal']

    def new_deal(self, card='', surrendered=None, doubled=None, stand=None, split=False):
        dealer_hand = self.dealer
        player_hands = self.player.copy()
        old_hand = self.next_hand
        sur = old_hand.surrendered if surrendered is None else surrendered
        dbl = old_hand.doubled if doubled is None else doubled
        std = old_hand.stand if stand is None else stand
        new_hand = self.next_hand.new_hand(card=card, surrendered=sur, doubled=dbl, stand=std, split=split)
        if self.next_player == 'Dealer':
            dealer_hand = new_hand
        else:
            if split:
                player_hands[self.next_hand_index] = new_hand[0]
                player_hands.append(new_hand[1])
            else:
                player_hands[self.next_hand_index] = new_hand
        return Deal(
            rules=self.rules.instreams,
            dealer_hand=dealer_hand.instreams,
            player_hands=tuple(ph.instreams for ph in player_hands)
        )

    @cached_property
    def next_states(self):
        if self.next_actions is None:
            return None
        result = {}
        for action in self.next_actions:
            if action == 'Deal':
                result['Deal'] = self.next_states_adding_card()
            elif action == 'Surrender':
                sub_deal = self.new_deal(surrendered=True)
                result['Surrender'] = {
                    'state': sub_deal,
                    'prob': 1.0,
                    'to_play': sub_deal.next_player,
                }
            elif action == 'Split':
                sub_deal = self.new_deal(split=True)
                result['Split'] = {
                    'state': sub_deal,
                    'prob': 1.0,
                    'to_play': sub_deal.next_player,
                }
            elif action == 'Double':
                result['Double'] = self.next_states_adding_card(doubled=True)
            elif action == 'Hit':
                result['Hit'] = self.next_states_adding_card()
            elif action == 'Stand':
                sub_deal = self.new_deal(stand=True)
                result['Stand'] = {
                    'state': sub_deal,
                    'prob': 1.0,
                    'to_play': sub_deal.next_player,
                }
            else:
                raise ValueError(f'Bad action "{action}"')
        return result

    def next_states_adding_card(self, doubled=None):
        # A Deal action gets a new card, so we enumerate states by new card.
        card_states = {}
        for card, prob in self.shoe.pdf.items():
            sub_deal = self.new_deal(card, doubled=doubled)
            card_states[card] = {
                'state': sub_deal,
                'prob': prob,
                'to_play': sub_deal.next_player,
            }
        return {
            'cards': card_states,
        }

    @cached_property
    def next_states_recursive(self):
        if self.next_states is None:
            return None
        result = {}
        for action, action_info in self.next_states.items():
            if 'cards' not in action_info and action_info['to_play'] is None:
                result[action] = action_info
            else:
                result[action] = {}
                if 'cards' not in action_info:
                    x = 3
                card_states = action_info['cards']
                for card, info in card_states.items():
                    result[action][card] = info
                    result[action][card]['actions'] = info['state'].next_states_recursive
        return result

    @cached_property
    def next_actions(self):
        if self.next_hand is None:
            return None
        return self.next_hand.actions

    @cached_property
    def next_hand(self):
        if self.next_player is None:
            return None
        elif self.next_player == 'Dealer':
            return self.dealer
        else:
            return self.player[self.next_hand_index]

    @cached_property
    def next_hand_index(self):
        if self.next_player != 'Player':
            return None
        for i, h in enumerate(self.player):
            if not h.is_done:
                return i

    @cached_property
    def next_player(self):
        # Deal phase
        if self.player[0].num_cards == 0:
            return 'Player'
        if self.dealer.num_cards == 0:
            return 'Dealer'
        if self.player[0].num_cards == 1:
            return 'Player'
        if self.dealer.num_cards == 1:
            return 'Dealer'

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
            if not h.is_done:
                return 'Player'
        if not self.dealer.is_done:
            return 'Dealer'
        return None

    def save(self):
        data = self.state_for_json()
        log(f'Saving {self.fpath}...')
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
        with open(self.fpath, 'w') as fp:
            json.dump(data, fp, indent=4)

    @cached_property
    def saved_state(self):
        if not os.path.isfile(self.fpath):
            return None
        log(f'Loading saved state {self.fpath}...')
        with open(self.fpath, 'r') as fp:
            state = json.load(fp)
        return state

    @property
    def splits(self):
        return len(self.player) - 1

    @property
    def state(self):
        result = {
            'summary': {
                'state': self.implied_name,
                'to_play': self.next_player,
            },
            'children': self.next_states_recursive,
            'player': [h.state for h in self.player],
            'dealer': self.dealer.state,
            'rules': self.rules.implied_name,
            'shoe': {
                'cards': self.shoe.cards,
                'pdf': self.shoe.pdf,
            },
        }
        if self.next_hand_index is not None:
            result['summary']['hand_index'] = self.next_hand_index
        return result

    def state_for_json(self, data=None):
        if data is None:
            data = self.state
        mod_data = {}
        for tag, val in data.items():
            if tag == 'state':
                mod_data[tag] = str(val)
            elif isinstance(val, dict):
                mod_data[tag] = self.state_for_json(val)
            else:
                mod_data[tag] = val
        return mod_data

    @property
    def terminal_value(self):
        if not self.is_done:
            return None
        val = 0
        for h in self.player:
            val += h.value
        return val


if __name__ == '__main__':
    deal = Deal.from_cards('T59T')
    deal.save()
