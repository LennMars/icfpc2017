import sys
import json
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

    def exec_move(self, move):
        if 'pass' in move:
            p = move['pass']['punter']
        elif 'claim' in move:
            p = move['claim']['punter']
            s = move['claim']['source']
            t = move['claim']['target']
            r = self.body[s][t]
            if r == RIVER_NEUTRAL:
                self.body[s][t] = p
                self.body[t][s] = p
            else:
                print('invalid move', file=sys.stderr)
        else:
            assert(False)

    def get_neutral_rivers(self):
        acc = []
        for s, neighbors in enumerate(self.body):
            for t in neighbors:
                if self.body[s][t] == RIVER_NEUTRAL:
                    acc.append((s, t))
        return acc

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

    def get_reachable_sites(self, mine, punter_id):
        maxint = 2 ** 31
        dists = [maxint] * self.num_sites
        dists[mine] = 0
        queue = []
        heapq.heappush(queue, (0, mine))
        while queue != []:
            _, u = heapq.heappop(queue)
            for t in self.body[u]:
                # Skip if the punter does not own the river.
                if self.body[u][t] != punter_id:
                    continue
                new_dist = dists[u] + 1
                if dists[t] > new_dist:
                    dists[t] = new_dist
                    heapq.heappush(queue, (new_dist, t))
        return [site for site, dist in enumerate(dists) if dist < maxint]

    def print_map(self):
        print('map:', self.body)

class PassPunter():
    def __init__(self, setup):
        pass

    def get_move(self, lmap):
        return {'pass': {'punter': p}}

class AlicePunter():
    def __init__(self, setup):
        self.punter_id = setup['punter']
        self.num_punters = setup['punters']
        self.turn = 0

    def get_move(self, lmap):
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
    def __init__(self, setup):
        self.punter_id = setup['punter']
        self.num_punters = setup['punters']
        self.turn = 0

    def get_move(self, lmap):
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

class EagerPunter():
    def __init__(self):
        pass

    def exec_setup(self, setup):
        self.punter_id = setup['punter']
        self.num_punters = setup['punters']
        self.lmap = ListMap(setup['map'])
        self.turn = 0

    def get_name(self):
        return 'test_punter'

    def get_move(self, prev_moves):
        for move in prev_moves:
            self.lmap.exec_move(move)
        rs = self.lmap.get_neutral_rivers()
        s, t = rs[0]
        self.turn += 1
        return {'claim': {'punter': self.punter_id, 'source': s, 'target': t}}

if __name__ == '__main__':
    with open('map/sample.json') as fp:
        map_ = json.load(fp)
    print(json.dumps(map_, indent=2))
    setup_alice = {'punter': 0,
                   'punters': 2,
                   'map': map_}
    setup_bob = {'punter': 1,
                 'punters': 2,
                 'map': map_}
    lmap = ListMap(map_)

    alice = AlicePunter(setup_alice)
    bob = BobPunter(setup_bob)
    for turn in range(6):
        move_alice = alice.get_move(None)
        print('move_alice:', move_alice)
        lmap.exec_move(move_alice)
        move_bob = bob.get_move(None)
        print('move_bob:', move_bob)
        lmap.exec_move(move_bob)
        lmap.print_map()

    punter_to_score = [0] * setup_alice['num_punters']
    for mine in lmap.mines:
        for punter in range(setup_alice['num_punters']):
            for site in lmap.get_reachable_sites(mine, punter):
                punter_to_score[punter] += lmap.mine_to_dists[mine][site] ** 2
    print('punter_to_score', punter_to_score)
