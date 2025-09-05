import sys
import random
import numpy as np
import pandas as pd

class Deck:
    def __init__(self):
        self.grave = None
        #frequency of each card number
        self.freq = {
            10: 21}
        self.freq = {
            0: 1,
            1: 5,
            2: 3,
            3: 3,
            4: 2,
            5: 2
        }
        for i in range(6, 11):
            self.freq[i] = 1
        
        #shuffle and fill deck
        self.reset()
    
    def reset(self):
        self.stack = []
        for n, f in self.freq.items():
            for i in range(f):
                self.stack.append(n)
        random.shuffle(self.stack)
        self.grave = self.stack.pop()
    
    def draw(self):
        return self.stack.pop()

class Agent:
    def __init__(self, play_values=None):
        self.play_values = self.random_play_values() if not play_values else play_values
        self.discard = []
        self.card = None
        self.second_card = None
        self.id = None
        self.deck = None
        self.game = None
        self.is_sheilded = False
    
    def random_play_values(self):
        return {i: random.uniform(0, 1) for i in range(11)}
    
    def mutate(self):
        i = random.choice(list(self.play_values.keys()))
        self.play_values[i] = random.uniform(0, 1)
    
    def get_opponents(self):
        return set(self.game.active_ids).difference(set([self.id]))
    
    def get_random_opp(self):
        id = random.choice(list(self.get_opponents()))
        return self.game.id_map[id]
    
    def draw(self):
        self.card = self.deck.draw()
    
    def grave_swap(self):
        temp = self.card
        self.card = self.deck.grave
        self.deck.grave = temp
        return 'grave swapped'
    
    def eight_swap(self, target):
        temp = self.card
        self.card = target.card
        target.card = temp
        return '8 swapped'
    
    def nine_swap(self):
        for a in self.game.agents:
            if a.card == 10:
                temp = self.card
                self.card = a.card
                a.card = temp
                return '9 swapped'
        return 'no 10 for 9 swap'
    
    def gain_sheild(self):
        self.is_sheilded = True
        return 'gained sheild'
    
    def do_five(self):
        if len(self.deck.stack) > 0:
            self.discard.append(self.card)
            self.draw()
            return '5 force played ' + str(self.discard[-1])
        return 'no cards to draw'
    
    def play(self):
        choice = self.card if self.play_values[self.card] > self.play_values[self.second_card] else self.second_card
        if choice == self.card:
            self.discard.append(self.card)
            self.card = self.second_card
            self.second_card = None
        else:
            self.discard.append(self.second_card)
            self.second_card = None
        self.game.report += '\nplayer ' + str(self.id) + ' plays ' + str(choice)
        return card_dict[choice].f(self, self.get_random_opp(), [random.uniform(0, 1)])

class Game:
    def __init__(self, agents):
        self.deck = Deck()
        self.agents = agents
        self.active_ids = []
        self.id_map = dict()
        self.active_i = 0
        self.report = 'New game'

        #set agent ids
        id_c = 0
        for a in self.agents:
            a.id = id_c
            a.game = self
            a.deck = self.deck
            a.draw()
            self.active_ids.append(id_c)
            self.add_id(id_c, a)
            id_c += 1
        
        self.input_index = {a.id: agents.index(a) for a in self.agents}
    
    def add_id(self, id, a):
        self.id_map[id] = a

    def eliminate(self, id):
        self.active_ids.remove(id)
        return 'elilminated player ' + str(id)
    
    def turn(self):
        a = self.id_map[self.active_ids[self.active_i]]
        a.second_card = self.deck.draw()
        if len(self.deck.stack) > 0:
            sub_message = a.play()
            self.report += '\n---' + sub_message if type(sub_message) == str else '\n---no message'
            self.active_i += 1
            self.active_i = 0 if self.active_i >= len(self.active_ids) else self.active_i

    def check_wins(self):
        if len(self.active_ids) == 1:
            self.report += '\n' + str(self.active_ids[0]) + ' wins!'
            return self.active_ids[0]
        if len(self.deck.stack) == 0:
            max_val = 0
            max_player = None
            for id in self.active_ids:
                a = self.id_map[id]
                if a.card > max_val:
                    max_val = a.card
                    max_player = id
                elif max_val == 10 and a.card == 0:
                    max_val = a.card
                    max_player = id
                    break
            self.report += '\n' + str(max_player) + ' wins!'
            return max_player
        return None
    
    def run(self):
        c = 0
        while c < 1000:
            self.turn()
            win = self.check_wins()
            if win != None:
                return win
            c += 1
        raise BufferError('over 1000 turns')

class Card:
    def __init__(self, val, f):
        self.val = val
        self.f = f
    
class Zero(Card):
    def __init__(self):
        f = lambda player, target, params: 'no effect'
        Card.__init__(self, 0, f)

class One(Card):
    def __init__(self):
        f = lambda player, target, params: game.eliminate(target.id) if target.card == np.round(params[0] * 21) else 'incorrect guess'
        Card.__init__(self, 1, f)

class Two(Card):
    def __init__(self):
        f = lambda player, target, params: game.deck.stack.insert(int(np.round(params[0] * 21)), game.deck.stack.pop())
        Card.__init__(self, 2, f)

class Three(Card):
    def f(self, player, target, params):
        if target.card < player.card:
            player.game.eliminate(target.id)
            return 'opp lower'
        elif player.card < target.card:
            player.game.eliminate(player.id)
            return 'self lower'
        else:
            return 'tie'

    def __init__(self):
        Card.__init__(self, 3, self.f)

class Four(Card):
    def __init__(self):
        f = lambda player, target, params: player.gain_sheild()
        Card.__init__(self, 4, f)

class Five(Card):
    def __init__(self):
        f = lambda player, target, params: player.get_random_opp().do_five()
        Card.__init__(self, 5, f)

class Six(Card):
    def __init__(self):
        f = lambda player, target, params: player.grave_swap() if params[0] > 0.5 else 'didnt swap'
        Card.__init__(self, 6, f)

class Seven(Card):
    def __init__(self):
        f = lambda player, target, params: [a.do_five() for a in player.game.agents]
        Card.__init__(self, 7, f)

class Eight(Card):
    def __init__(self):
        f = lambda player, target, params: player.eight_swap(player.get_random_opp())
        Card.__init__(self, 8, f)

class Nine(Card):
    def f(self, player, target, params):
        for a in player.game.agents:
            if a.card == 10:
                player.eight_swap(a)
                return str(a.id) + ' had the 10 and swapped with ' + str(player.id)
        return 'no one had the 10 ten'

    def __init__(self):
        Card.__init__(self, 9, self.f)

class Ten(Card):
    def __init__(self):
        f = lambda player, target, params: player.game.eliminate(player.id)
        Card.__init__(self, 10, f)

card_dict = {
    0: Zero(),
    1: One(),
    2: Two(),
    3: Three(),
    4: Four(),
    5: Five(),
    6: Six(),
    7: Seven(),
    8: Eight(),
    9: Nine(),
    10: Ten(),
}

if __name__ == '__main__':

    #train
    cycles = 1000
    game_size = 3
    n_agents = 50
    values = [{i: (10 - i) / 10 for i in range(11)} for n in range(50)]
    
    for n in range(cycles):
        if n % 100 == 0:
            print('training... ' + str(n) + '/' + str(cycles), end='\r', file=sys.stdout, flush=True)
        random.shuffle(values)
        for i in range(int(len(values) / game_size)):
            wins = {i: 0 for i in range(game_size)}
            for g in range(10):
                agents = [Agent(values[i * 2 + a_i]) for a_i in range(game_size)]
                game = Game(agents)
                try:
                    winner = game.input_index[game.run()]
                except Exception as e:
                    print(e)
                    print('Error in game:')
                    print(game.report)
                    exit()
                wins[winner] += 1
            new_values = np.average([list(a.play_values.values()) for a in agents], weights=list(wins.values()), axis=0)
            new_values = {i: new_values[i] for i in range(len(new_values))}
            for a_i in range(game_size - 1):
                values[i * 2 + a_i] = new_values
            a = Agent(new_values)
            a.mutate()
            values[i * 2 + game_size - 1] = a.play_values
    
    #print the mean values across all agents
    print('mean values across all agents:')
    mean_vals = np.mean([list(v.values()) for v in values], axis=0)
    print({i: str(round(mean_vals[i], 2)) for i in range(len(mean_vals))})

    #print last game report
    #print(game.report)

    #print dataframe of all agents and their values
    #print(pd.DataFrame(data=np.transpose([[round(n, 3) for n in v.values()] for v in values]), index=values[0].keys()))