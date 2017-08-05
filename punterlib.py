import copy
import sys
import json
import heapq
from typing import Dict, Tuple, List

RIVER_NEUTRAL = -1

def send_in_json(subp, buf):
    subp.stdin.write((json.dumps(buf) + '\n').encode())
    subp.stdin.flush()

def send_in_json_std(buf):
    print(json.dumps(buf), file=sys.stdout)
    sys.stdout.flush()

def recv_in_json(subp):
    msg = subp.stdout.readline().strip()
    return json.loads(msg.decode())

def recv_in_json_std():
    msg = sys.stdin.readline()
    return json.loads(msg)

class ListMap():
    sites: List[int]
    rivers: List
    mines: List[int]
    num_punters: int
    num_sites: int
    # body: s-th entry is Dict[target, state of river (s, target)].
    body: List[Dict[int, int]]
    # mine_to_dists[m][site] is distance from m-th mine to the site.
    mine_to_dists: Dict[int, List[int]]

    def __init__(self) -> None:
        pass

    def exec_setup(self, setup: Dict) -> None:
        self.sites = setup['map']['sites']
        self.rivers = setup['map']['rivers']
        self.mines = setup['map']['mines']
        self.num_punters = setup['punters']

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
        print('[INFO] mine_to_dists:', self.mine_to_dists, file=sys.stderr)

    def normalize_key(self):
        for s in range(self.num_sites):
            normalized = {}
            for t in self.body[s].keys():
                normalized[int(t)] = self.body[s][t]
            self.body[s] = normalized

    def num_rivers(self):
        return len(self.rivers)

    def exec_move(self, move: Dict) -> None:
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
                print('[Warning] invalid move', file=sys.stderr)
        else:
            assert(False)

    def get_neutral_rivers(self) -> List[Tuple[int, int]]:
        acc = []
        for s, neighbors in enumerate(self.body):
            for t in neighbors:
                if self.body[s][t] == RIVER_NEUTRAL:
                    acc.append((s, t))
        return acc

    def get_mine_to_dists(self, mine: int) -> List[int]:  # By Dijkstra method.
        dists = [2 ** 31] * self.num_sites
        prevs = [-1] * self.num_sites  # -1: no prev.
        dists[mine] = 0
        queue: List[Tuple[int, int]] = []
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

    def get_reachable_sites(self, mine: int, punter_id: int) -> List[int]:
        maxint = 2 ** 31
        dists = [maxint] * self.num_sites
        dists[mine] = 0
        queue: List[Tuple[int, int]] = []
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

    def print_map(self) -> None:
        print('[INFO] map:', self.body, file=sys.stderr)

    def dump(self):
        self_dict = {'sites': copy.deepcopy(self.sites),
                     'rivers': copy.deepcopy(self.rivers),
                     'mines': copy.deepcopy(self.mines),
                     'num_punters': self.num_punters,
                     'num_sites': self.num_sites,
                     'body': copy.deepcopy(self.body),
                     'mine_to_dists': copy.deepcopy(self.mine_to_dists)}
        return self_dict

    def get_punter_to_score(self) -> List[int]:
        punter_to_score = [0] * self.num_punters
        for mine in self.mines:
            for punter in range(self.num_punters):
                for site in self.get_reachable_sites(mine, punter):
                    punter_to_score[punter] += self.mine_to_dists[mine][site] ** 2
        return punter_to_score

def recover_listmap(state):
    lmap = ListMap()
    lmap.sites = state['sites']
    lmap.rivers = state['rivers']
    lmap.mines = state['mines']
    lmap.num_punters = state['num_punters']
    lmap.num_sites = state['num_sites']
    lmap.body = state['body']
    lmap.normalize_key()
    lmap.mine_to_dists = state['mine_to_dists']
    return lmap

class PunterBase():
    punter_id: int
    num_punters: int
    lmap: ListMap

    def __init__(self) -> None:
        pass

    def get_name(self) -> str:
        raise(NotImplementedError)

    def exec_setup(self, setup) -> None:
        self.punter_id = setup['punter']
        self.num_punters = setup['punters']
        self.lmap = ListMap()
        self.lmap.exec_setup(setup)

    def get_move(self, prev_moves) -> Dict:
        raise(NotImplementedError)

    def recover_state(self, state) -> None:
        raise(NotImplementedError)

    def exec_all(self):
        # Handshake.
        name = self.get_name()
        send_in_json_std({'me': name})
        msg = recv_in_json_std()
        assert(msg['you'] == name)
        # Switch between Setup and Gameplay.
        msg = recv_in_json_std()
        if 'punter' in msg:  # Setup.
            ready = self.exec_setup(msg)
            assert(type(ready['ready']) == int)
            send_in_json_std(ready)
        elif 'move' in msg:  # Gameplay.
            self.recover_state(msg['state'])
            assert(type(self.punter_id) == int)
            assert(type(self.num_punters) == int)
            assert(type(self.lmap) == ListMap)
            move = self.get_move(msg['move']['moves'])
            state = self.dump_state()
            assert(type(state['punter_id']) == int)
            assert(type(state['num_punters']) == int)
            assert(type(state['lmap']) == dict)
            send_in_json_std(move)
            send_in_json_std({'state': state})
        else:
            assert(False)

class PassPunter(PunterBase):
    def __init__(self):
        pass

    def get_name(self):
        return 'passer'

    def exec_setup(self, setup):
        super(PassPunter, self).exec_setup(setup)

    def get_move(self, prev_moves):
        return {'pass': {'punter': p}}

class AlicePunter(PunterBase):
    def __init__(self):
        self.turn = 0

    def get_name(self):
        return 'alice'

    def exec_setup(self, setup):
        super(AlicePunter, self).exec_setup(setup)

    def get_move(self, prev_moves):
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

class BobPunter(PunterBase):
    def __init__(self):
        self.turn = 0

    def get_name(self):
        return 'bob'

    def exec_setup(self, setup):
        super(BobPunter, self).exec_setup(setup)

    def get_move(self, prev_moves):
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

if __name__ == '__main__':
    with open('map/sample.json') as fp:
        map_ = json.load(fp)
    setup_alice = {'punter': 0,
                   'punters': 2,
                   'map': map_}
    setup_bob = {'punter': 1,
                 'punters': 2,
                 'map': map_}
    lmap = ListMap()
    lmap.exec_setup(setup_alice)

    alice = AlicePunter()
    bob = BobPunter()
    alice.exec_setup(setup_alice)
    bob.exec_setup(setup_bob)

    map_log = []
    for turn in range(6):
        move_alice = alice.get_move(None)
        print('[INFO] move_alice:', move_alice, file=sys.stderr)
        lmap.exec_move(move_alice)
        move_bob = bob.get_move(None)
        print('[INFO] move_bob:', move_bob, file=sys.stderr)
        lmap.exec_move(move_bob)
        map_log.append(lmap.dump())

    print('[INFO] punter_to_score', lmap.get_punter_to_score(), file=sys.stderr)
    print('[INFO] output map log', file=sys.stderr)
    with open('map.log', 'w') as fp:
        json.dump(map_log, fp)
