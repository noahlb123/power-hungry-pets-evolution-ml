import index
import numpy as np

'''
Format
Nodes (6082560 game nodes expected)
    int: game state
    float: p win higher
    float: p win lower
Edges (about 10 * n_nodes)
    float: p occurance
    bool: lower / higher
Objects
    dict: game state to node and edges
    set: leading node game states
    set: complete nodes game states
'''

class NodeReader:
    def __init__(self):
        self.cards = set()
        for i in range(1, 6):
            for card in range(1, 6):
                if (card == 1) or (card in (2, 3) and i <= 3) or (card in (4, 5) and i <= 2):
                    mod = i * 10 if (i - 1) else 0
                    self.cards.add(card + mod)
    
    def compress_game_state(self, state_tuple):
        hand, discard, possibilities, discard_digits, dis_arr, pos_arr = state_tuple
        if 10 in hand:
            game_state = int(''.join([str(i) for i in [hand[0], 9] + discard_digits + [1]]))
        else:
            game_state = int(''.join([str(i) for i in hand + discard_digits + [0]]))
        return game_state

    def expand_game_state(self, game_state):
        #game_state explination:
        #digits 1-2: lower and greater cards in hand
        #digit 14: boolean representing if a 10 is in hand
        #digits 3-13: starting at 0, each index represents a card value and its digit represents its number in the discard
        digits = [int(d) for d in str(game_state)]
        hand = [i for i in digits[0:2]]
        hand = [min(hand), max(hand)] if not digits[13] else [min(hand), 10]
        discard_digits = digits[2:13]
        discard = set()
        possibilities = set()
        for i in range(11):
            digit = discard_digits[i]
            if digit:
                for n in range(1, digit + 1):
                    mod = n * 10 if (n - 1) else 0
                    discard.add(i + mod)
        possibilities = self.cards.difference(discard)
        dis_arr = [i % 10 if i != 10 else 10 for i in discard]
        pos_arr = [i % 10 if i != 10 else 10 for i in possibilities]
        return hand, discard, possibilities, discard_digits, dis_arr, pos_arr


if __name__ == '__main__':
    n_nodes = 2 * 10 * 11 * np.prod([v + 1 for v in index.Deck().freq.values()])
    mean_edges = 10 * np.mean([1, 2, 1, 3, 1, 11, 1, 11, 11, 2, 1])
    print('nodes in graph:', n_nodes)
    print('mean number of edges per node:', mean_edges)
    print('minimum size of solution in Gb:', n_nodes * mean_edges / (10 ** 9))
    print('solution using np ndarray (Tb):', n_nodes ** 2 / (10 ** 12))
    print('solution using raw text (Gb):', 3 * n_nodes * mean_edges / (10 ** 9))

    game_state = 89153322111110
    nr = NodeReader()
    print(nr.expand_game_state(game_state))
    print(nr.compress_game_state(nr.expand_game_state(game_state)) == game_state)
    print(nr.compress_game_state(nr.expand_game_state(game_state)), game_state)

    c = 0
    try:
        print('press ^C to save progress at anytime...')
        while True:
            c += 1
    except KeyboardInterrupt: #catch ctrl c to save progress
        print()
        print('saving...')
        exit()