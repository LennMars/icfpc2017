import sys
import json
#import numpy as np
import typing
import heapq

RIVER_NEUTRAL = -1

class ListMap():
    def __init__(self, map_):
        self.sites = map_['sites']
        self.rivers = map_['rivers']
        self.mines = map_['mines']

        self.num_sites = len(self.sites)
        self.body = []
        for _ in range(self.num_sites):
            self.body.append({})
        for r in self.rivers:
            s = r['source']
            t = r['target']
            self.body[s][t] = RIVER_NEUTRAL
            self.body[t][s] = RIVER_NEUTRAL
        self.mine_to_dists = {}
        for mine in self.mines:
            self.mine_to_dists[mine] = self.get_mine_to_dists(mine)
        print('mine_to_dists:', self.mine_to_dists)

    def get_mine_to_dists(self, mine):  # By Dijkstra method.
        dists = [2 ** 31] * self.num_sites
        prevs = [-1] * self.num_sites  # -1: no prev.
        dists[mine] = 0
        queue = []
        heapq.heappush(queue, (0, mine))
        while queue != []:
            _, u = heapq.heappop(queue)
            for t in self.body[u]:
                if prevs[t] != -1:
                    continue
                new_dist = dists[u] + 1
                if dists[t] > new_dist:
                    dists[t] = new_dist
                    prevs[t] = u
                    heapq.heappush(queue, (new_dist, t))
        return dists

    def get_reachable_sites(self, mine, punter):
        maxint = 2 ** 31
        dists = [maxint] * self.num_sites
        dists[mine] = 0
        queue = []
        heapq.heappush(queue, (0, mine))
        while queue != []:
            _, u = heapq.heappop(queue)
            for t in self.body[u]:
                # Skip if the punter does not own the river.
                if self.body[u][t] != punter:
                    continue
                new_dist = dists[u] + 1
                if dists[t] > new_dist:
                    dists[t] = new_dist
                    heapq.heappush(queue, (new_dist, t))
        return [site for site, dist in enumerate(dists) if dist < maxint]

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
        self.lmap = ListMap(setup['map'])

    def exec_move(self, move):
        if 'pass' in move:
            p = move['pass']['punter']
        elif 'claim' in move:
            p = move['claim']['punter']
            s = move['claim']['source']
            t = move['claim']['target']
            r = self.lmap.body[s][t]
            if r == RIVER_NEUTRAL:
                self.lmap.body[s][t] = p
                self.lmap.body[t][s] = p
            else:
                print('invalid move', file=sys.stderr)
        else:
            assert(False)

    def print_state(self):
        #print('punter: {:d}, punters: {:d}'.format(self.punter, self.punters))
        print('map:')
        print(self.lmap.body)

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

    punter_to_score = [0] * state.punters
    for mine in state.lmap.mines:
        for punter in range(state.punters):
            for site in state.lmap.get_reachable_sites(mine, punter):
                punter_to_score[punter] += state.lmap.mine_to_dists[mine][site] ** 2
    print('punter_to_score', punter_to_score)
