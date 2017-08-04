import sys
import json
import numpy as np
import typing

RIVER_EMPTY = -2
RIVER_NEUTRAL = -1

class ArrayMap():
    def __init__(self, map_):
        self.sites = map_['sites']
        self.rivers = map_['rivers']
        self.mines = map_['mines']

        self.num_sites = len(self.sites)
        self.array = np.zeros((self.num_sites, self.num_sites), dtype=int)
        self.array[:, :] = RIVER_EMPTY
        for r in self.rivers:
            s = r['source']
            t = r['target']
            self.array[s, t] = RIVER_NEUTRAL
            self.array[t, s] = RIVER_NEUTRAL

class PassPunter():
    def __init__(self):
        pass

    def get_move(self, state):
        return {'pass': {'punter': p}}

class AlicePunter():
    def __init__(self, punter):
        self.punter = punter
        self.turn = 0
        pass

    def get_move(self, state):
        if self.turn == 0:
            move = {'claim': {'punter': 0, 'source': 0, 'target': 1}}
        elif self.turn == 1:
            move = {'claim': {'punter': 0, 'source': 2, 'target': 3}}
        elif self.turn == 2:
            move = {'claim': {'punter': 0, 'source': 4, 'target': 5}}
        elif self.turn == 3:
            move = {'claim': {'punter': 0, 'source': 6, 'target': 7}}
        elif self.turn == 4:
            move = {'claim': {'punter': 0, 'source': 1, 'target': 3}}
        elif self.turn == 5:
            move = {'claim': {'punter': 0, 'source': 5, 'target': 7}}
        self.turn += 1
        return move

class BobPunter():
    def __init__(self, punter):
        self.punter = punter
        self.turn = 0
        pass

    def get_move(self, state):
        if self.turn == 0:
            move = {'claim': {'punter': 1, 'source': 1, 'target': 2}}
        elif self.turn == 1:
            move = {'claim': {'punter': 1, 'source': 3, 'target': 4}}
        elif self.turn == 2:
            move = {'claim': {'punter': 1, 'source': 5, 'target': 6}}
        elif self.turn == 3:
            move = {'claim': {'punter': 1, 'source': 7, 'target': 0}}
        elif self.turn == 4:
            move = {'claim': {'punter': 1, 'source': 3, 'target': 5}}
        elif self.turn == 5:
            move = {'claim': {'punter': 1, 'source': 7, 'target': 1}}
        self.turn += 1
        return move

class State():
    def __init__(self, setup):
        self.punter = setup['punter']
        self.punters = setup['punters']
        self.amap = ArrayMap(setup['map'])

    def exec_move(self, move):
        if 'pass' in move:
            p = move['pass']['punter']
        elif 'claim' in move:
            p = move['claim']['punter']
            s = move['claim']['source']
            t = move['claim']['target']
            r = self.amap.array[s, t]
            if r == RIVER_NEUTRAL:
                self.amap.array[s, t] = p
                self.amap.array[t, s] = p
            else:
                print('invalid move', file=sys.stderr)
        else:
            assert(False)

    def print_state(self):
        #print('punter: {:d}, punters: {:d}'.format(self.punter, self.punters))
        print('map:')
        print(self.amap.array)

if __name__ == '__main__':
    with open('map/sample.json') as fp:
        map_ = json.load(fp)
    print(json.dumps(map_, indent=2))
    setup = {'punter': 0,
             'punters': 2,
             'map': map_}
    state = State(setup)

    alice = AlicePunter(0)
    bob = BobPunter(1)
    for turn in range(6):
        move_alice = alice.get_move(state)
        print('move_alice:', move_alice)
        state.exec_move(move_alice)
        state.print_state()
        move_bob = bob.get_move(state)
        print('move_bob:', move_bob)
        state.exec_move(move_bob)
        state.print_state()
