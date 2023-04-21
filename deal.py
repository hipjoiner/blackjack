from functools import cache, cached_property
import json
import os
import sys

from config import CachedInstance, home_dir, log, log_occasional
from hand import Hand
from rules import Rules
from shoe import Shoe


class Deal(metaclass=CachedInstance):
    node_threshold = 300

    def __init__(
        self,
        rules=(1.5, 6, False, 'Any2', 3, True, True, True),
        dealer_hand=((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), False, False, False),
        player_hands=(((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), False, False, False),)
    ):
        self.rules = Rules(*rules)
        self.shoe = Shoe(self)
        self.dealer = Hand(self, 'Dealer', *dealer_hand)
        self.player = sorted([Hand(self, 'Player', *ph) for ph in player_hands])

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
        return f'{self.rules.implied_name} [{str(self.dealer)}] {" ".join(str(h) for h in self.player)}'

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
        """Instantiate a child state from this one, with modifications as specified in args."""
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
        d = Deal(
            rules=self.rules.instreams,
            dealer_hand=dealer_hand.instreams,
            player_hands=tuple(ph.instreams for ph in player_hands)
        )
        log_occasional(d)
        return d

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
    def next_is_down_card_deal(self):
        return self.next_actions == ['Deal'] and self.next_player == 'Dealer' and self.dealer.num_cards == 1

    @cached_property
    def next_is_down_card_turn(self):
        result = self.next_actions == ['Turn']
        return result

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

    @cached_property
    def next_states(self):
        if self.next_actions is None:
            return None
        result = {}
        for action in self.next_actions:
            if action == 'Deal':
                result['Deal'] = self.next_states_adding_card()
            elif action == 'Turn':
                result['Turn'] = self.next_states_adding_card()
            elif action == 'Surrender':
                result['Surrender'] = {
                    '<no card>': {
                        'state': self.new_deal(surrendered=True),
                        'prob': 1.0,
                    }
                }
            elif action == 'Split':
                result['Split'] = {
                    '<no card>': {
                        'state': self.new_deal(split=True),
                        'prob': 1.0,
                    }
                }
            elif action == 'Double':
                result['Double'] = self.next_states_adding_card(doubled=True)
            elif action == 'Hit':
                result['Hit'] = self.next_states_adding_card()
            elif action == 'Stand':
                result['Stand'] = {
                    '<no card>': {
                        'state': self.new_deal(stand=True),
                        'prob': 1.0,
                    }
                }
            else:
                raise ValueError(f'Bad action "{action}"')
        return result

    def next_states_adding_card(self, doubled=None):
        # A Deal action gets a new card, so we enumerate states by new card.
        card_states = {}
        pdf = self.shoe.pdf
        if self.next_is_down_card_deal:
            """If up card is a T, then down card is either
                    A (Blackjack, hand over) or 
                    x (unknown, play on)
                If up card is an A, then down card is either a 
                    T (Blackjack, hand over) or 
                    x (unknown, play on)
                FIXME: Later, when it's Dealer's turn to play, we turn over the x to reveal
                    If up card is a T, down card is something from 2 to T (no A)
                    If up card is an A, down card is something from 2 to 9 or A (no T)
            """
            if self.dealer.cards == 'T':
                pdf = {
                    'A': pdf['A'],
                    'x': 1 - pdf['A'],
                }
            elif self.dealer.cards == 'A':
                pdf = {
                    'T': pdf['T'],
                    'x': 1 - pdf['T'],
                }
        elif self.next_is_down_card_turn:
            if self.dealer.cards[0] == 'T':
                # If up card is a T and we're still playing, down card can't be an A.
                adj_factor = pdf['A']
                pdf = {c: p / (1 - adj_factor) for c, p in pdf.items()}
                del pdf['A']
            elif self.dealer.cards[0] == 'A':
                # If up card is an A and we're still playing, down card can't be a T.
                adj_factor = pdf['T']
                pdf = {c: p / (1 - adj_factor) for c, p in pdf.items()}
                del pdf['T']
        for card, prob in pdf.items():
            if prob <= 0:
                continue
            sub_deal = self.new_deal(card, doubled=doubled)
            card_states[card] = {
                'state': sub_deal,
                'prob': prob,
            }
        return card_states

    def save(self, save_valuation=False):
        data = self.state_for_json
        if save_valuation:
            data['valuation'] = self.valuation
        os.makedirs(os.path.dirname(self.fpath), exist_ok=True)
        with open(self.fpath, 'w') as fp:
            json.dump(data, fp, indent=4)

    @property
    def splits(self):
        return len(self.player) - 1

    @cached_property
    def state(self):
        result = {
            'summary': {
                'state': self.implied_name,
                'to_play': self.next_player,
                'hand_index': self.next_hand_index,
            },
            'children': self.next_states,
            'player': [h.state for h in self.player],
            'dealer': self.dealer.state,
            'rules': self.rules.implied_name,
            'shoe': {
                'cards': self.shoe.cards,
                'pdf': self.shoe.pdf,
            },
            'valuation_leaf': self.valuation_leaf,
        }
        return result

    @cached_property
    def state_for_json(self):
        result = self.state_for_json_recursive(self.state)
        return result

    def state_for_json_recursive(self, data=None):
        if data is None:
            data = self.state
        mod_data = {}
        for tag, val in data.items():
            if isinstance(val, Deal):
                mod_data[tag] = str(val)
            elif isinstance(val, dict):
                mod_data[tag] = self.state_for_json_recursive(val)
            else:
                mod_data[tag] = val
        return mod_data

    @cached_property
    def valuation_leaf(self):
        """If all hands in this state are terminal and the outcome of all can be determined,
            compute the total bet value returned to Player of all hands, and return.
            Otherwise, return None.
        """
        val = {
            'value': 0,
            'nodes': 1,
            'hands': [],
        }
        for h in self.player:
            if h.valuation_leaf is None:
                return None
            val['hands'].append(h.valuation_leaf)
            val['value'] += h.valuation_leaf['value']
        return val

    @cached_property
    def valuation(self):
        """Compute value to Player, and number of child nodes, recursively.
            If I have a leaf value, return that value (1 node).
            If no leaf value, I must have child states:
                At action levels, choose highest-value action, noting its value and node count
                At card pdf levels, compute a weighted average value based on probabilities of each card
                    and value of resulting state
        """
        # log(f'{self.implied_name} valuation...')
        if self.valuation_leaf is not None:
            # log(f'{self.implied_name} valuation OK')
            return {'Summary': self.valuation_leaf}
        result = {}
        best_action = {
            'value': -99,
            'nodes': None,
        }
        for action, state_data in self.next_states.items():
            val_tot = 0
            node_tot = 0
            for card, card_data in state_data.items():
                child_state = card_data['state']

                """If child has valuation already saved to disk, retrieve and use that instead."""
                child_val_cached = child_state.valuation_saved
                if child_val_cached is not None:
                    log(f'Using cached valuation for {child_state.implied_name}...')
                    child_val = child_val_cached
                else:
                    child_val = child_state.valuation['Summary']

                val_tot += card_data['prob'] * child_val['value']
                node_tot += child_val['nodes']

                """Cache valuations with lots of nodes for later retrieval"""
                if child_val['nodes'] >= self.node_threshold and not child_val_cached:
                    log(f'Saving computed valuation for {child_state.implied_name} ({child_val["nodes"]} nodes)...')
                    child_state.save(save_valuation=True)

            result[action] = {
                'value': val_tot,
                'nodes': node_tot,
            }
            if result[action]['value'] > best_action['value']:
                best_action = result[action]
        result['Summary'] = best_action
        # log(f'{self.implied_name} valuation OK')
        return result

    @property
    def valuation_saved(self):
        # If I previously saved valuation, load and use that
        if os.path.isfile(self.fpath):
            with open(self.fpath, 'r') as fp:
                saved_data = json.load(fp)
            if 'valuation' in saved_data:
                return saved_data['valuation']['Summary']
        return None


if __name__ == '__main__':
    cards = '9T'
    if len(sys.argv) > 1:
        cards = sys.argv[1]
    deal = Deal.from_cards(cards=cards)
    deal.save(save_valuation=True)
