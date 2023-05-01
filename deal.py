from functools import cache, cached_property
import gc
import json
import os
import sys

from config import home_dir, log, log_occasional, show_deal_refs
from node import Node
from hand import Hand
from rules import Rules
from shoe import Shoe


class Deal(Node):
    node_save_threshold = 25000
    # cache_limit = 4000000
    cache_limit = 3000000

    def __init__(
        self,
        rules=(1.5, 6, False, 'Any2', 3, True, True, True),
        dealer=((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), False, '', 0, False, False),
        player=((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), False, '', 0, False, False),
        true_count=0,
    ):
        self.rules = Rules(*rules)
        self.shoe = Shoe(self, true_count=true_count)
        self.dealer = Hand(self, 'Dealer', *dealer)
        self.player = Hand(self, 'Player', *player)

    def __repr__(self):
        return self.implied_name

    def clear(self, indent=0):
        """Blow this object out of memory. Also do any child states recursively."""
        if self.next_states is not None:
            for child_data in self.next_states.values():
                for card_data in child_data.values():
                    child = card_data['state']
                    child.clear(indent=indent + 2)
                    del child
        self.shoe.deal = None
        self.player.deal = None
        self.dealer.deal = None
        super().clear()
        Node.pop_reference(self)

    @property
    def fpath(self):
        rule_dir = str(self.rules)
        count_dir = f'TC{self.shoe.true_count}'
        cards_dir = self.dealer.cards[:2]
        if self.dealer.num_cards > 0:
            return f'{home_dir}/states/{rule_dir}/{count_dir}/{cards_dir}/{self.implied_name}.json'
        return f'{home_dir}/states/{rule_dir}/{count_dir}/{self.implied_name}.json'

    @staticmethod
    def from_cards(cards, true_count=0):
        """Instantiate a Deal state using the cards supplied as if dealt in order."""
        d = Deal(true_count=true_count)
        for c in cards:
            d = d.new_deal(c)
        return d

    @property
    def implied_name(self):
        return f'{self.rules.implied_name} TC{self.shoe.true_count:+d} [{str(self.dealer)}] {str(self.player)}'

    @property
    def is_done(self):
        return self.next_hand is None

    def load(self):
        if not os.path.isfile(self.fpath):
            return None
        with open(self.fpath, 'r') as fp:
            contents = json.load(fp)
        return contents['deal']

    def new_deal(self, card='', surrendered=None, split=False, doubled=None, stand=None):
        """Check cache size first; if too large, exit to avoid memory overflow"""
        cache_size = len(self.__class__._instances)
        if cache_size > self.cache_limit:
            log(f'Cache size {cache_size} > limit of {self.cache_limit}; exiting for restart...')
            sys.exit(0)
        """Instantiate child state from this one, with modifications as specified in args."""
        current_hand = self.next_hand
        sur = current_hand.surrendered if surrendered is None else surrendered
        dbl = current_hand.doubled if doubled is None else doubled
        std = current_hand.stand if stand is None else stand
        new_hand = current_hand.new_hand(card=card, surrendered=sur, split=split, doubled=dbl, stand=std)
        if self.next_player == 'Dealer':
            d = Deal(
                rules=self.rules.instreams,
                dealer=new_hand.instreams,
                player=self.player.instreams,
                true_count=self.shoe.true_count,
            )
        else:
            d = Deal(
                rules=self.rules.instreams,
                dealer=self.dealer.instreams,
                player=new_hand.instreams,
                true_count=self.shoe.true_count,
            )
        log_occasional(f'Instantiated {d} ({cache_size} in cache)', seconds=10)
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
            return self.player

    @cached_property
    def next_is_down_card_deal(self):
        return self.next_actions == ['Deal'] and self.next_player == 'Dealer' and self.dealer.num_cards == 1

    @cached_property
    def next_is_down_card_turn(self):
        result = self.next_actions == ['Turn']
        return result

    @property
    def next_player(self):
        # Deal phase
        if self.player.num_cards == 0:
            return 'Player'
        if self.dealer.num_cards == 0:
            return 'Dealer'
        if self.player.num_cards == 1:
            return 'Player'
        if self.dealer.num_cards == 1:
            return 'Dealer'
        # Check for Blackjacks
        if self.dealer.is_blackjack:
            return None
        if self.player.is_blackjack:
            return None
        # If player busted or surrendered, dealer doesn't play
        if self.player.is_busted or self.player.surrendered:
            return None
        if not self.player.is_done:
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
                if not self.player.is_done:
                    raise ValueError(f'Bad state ordering: {self.implied_name}')
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
            else:
                pdf = {
                    'x': 1.0,
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
            else:
                pass    # Shoe pdf is correct; no reweighting required
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

    def show_refs(self):
        """WARNING: VERY SLOW"""
        gc.collect()
        objs = gc.get_objects()
        for i, o in enumerate(objs):
            if self == o:
                log(f'References for {self.implied_name}:')
                log(f'  Object {i + 1} ({str(o)})')
                for j, ref in enumerate(gc.get_referrers(o)):
                    log(f'  Ref {j + 1}: {str(ref)[:300]}')

    @cached_property
    def state(self):
        result = {
            'summary': {
                'state': self.implied_name,
                'to_play': self.next_player,
            },
            'children': self.next_states,
            'player': self.player.state,
            'dealer': self.dealer.state,
            'rules': self.rules.implied_name,
            'shoe': {
                'cards': self.shoe.cards,
                'true_count': self.shoe.true_count,
                'pdf': self.shoe.pdf,
            },
            'valuation_leaf': self.valuation_leaf,
        }
        return result

    @property
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
        v = self.player.valuation_leaf
        if v is None:
            return None
        v['nodes'] = 1
        return v

    @cached_property
    def valuation(self):
        """Compute value to Player, and number of child nodes, recursively.
            If I have a leaf value, return that value (1 node).
            If no leaf value, I must have child states:
                At action levels, choose highest-value action, noting its value and node count
                At card pdf levels, compute a weighted average value based on probabilities of each card
                    and value of resulting state
        """
        if self.valuation_leaf is not None:
            # log(f'{self.implied_name} valuation OK')
            return [self.valuation_leaf]
        results = []
        for action, state_data in self.next_states.items():
            val_tot = 0
            node_tot = 0
            for card, card_data in state_data.items():
                child_state = card_data['state']
                """If child has valuation already saved to disk, retrieve and use that instead."""
                if 'valuation' in child_state.__dict__:             # Already computed & cached in memory
                    # log(f'Using cached valuation for {child_state.implied_name}...')
                    child_val = child_state.valuation
                elif child_state.valuation_is_saved:                # Already computed & saved to disk
                    child_val = child_state.valuation_saved
                    log(f'Using saved valuation for {child_state.implied_name}...')
                else:
                    child_val = child_state.valuation               # Not yet computed; compute

                """If valuation is for a starting hand or has many many nodes, save for later use"""
                if not child_state.valuation_is_saved:
                    max_nodes = 0
                    for child in child_val:
                        max_nodes = max(max_nodes, child['nodes'])
                    if max_nodes >= self.node_save_threshold:
                        log(f'Saving {child_state.implied_name} ({max_nodes} max nodes)...')
                        child_state.save(save_valuation=True)
                    # We care particularly about starting hands
                    elif child_state.player.num_cards <= 2 and child_state.dealer.num_cards <= 2 and not (
                        child_state.player.surrendered or
                        child_state.player.split_count > 0 or
                        child_state.player.doubled or
                        child_state.player.stand
                    ):
                        log(f'Saving starting hand {child_state.implied_name} ({max_nodes} max nodes)...')
                        child_state.save(save_valuation=True)

                val_tot += card_data['prob'] * child_val[0]['value']
                node_tot += child_val[0]['nodes']
            result = {
                'action': action,
                'value': val_tot,
                'nodes': node_tot,
            }
            results.append(result)
        results = sorted(results, key=lambda r: r['value'], reverse=True)
        self.invalidate('next_states')
        return results

    @property
    def valuation_is_saved(self):
        return os.path.isfile(self.fpath)

    @property
    def valuation_saved(self):
        # If I previously saved valuation, load and use that
        if os.path.isfile(self.fpath):
            try:
                with open(self.fpath, 'r') as fp:
                    saved_data = json.load(fp)
            except json.decoder.JSONDecodeError as e:
                log(f'ERROR: {self.fpath} failed to load')
                raise e
            if 'valuation' in saved_data:
                return saved_data['valuation']
        return None


if __name__ == '__main__':
    pass
