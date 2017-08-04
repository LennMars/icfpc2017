import json
import numpy as np
import typing

def read_map(map_):
    return map_

class PassPunter():
    def __init__(self):
        pass

    def get_move(p, state):
        return {'pass': {'punter': p}}

class State():
    def __init__(self, setup):
        self.punter = setup['punter']
        self.punters = setup['punters']
        self.amap = read_map(setup['map'])

    def exec_moves(moves):
        for m in moves:
            if 'pass' in m:
                p = m['punter']
            elif 'claim' in m:
                p = m['punter']
                s = m['source']
                t = m['target']
            else:
                assert(False)

class Communicator():
    def __init__(self, name):
        self.name = name

if __name__ == '__main__':
    with open('map/sample.json') as fp:
        map_ = json.load(fp)
    print(json.dumps(map_, indent=2))
    setup = {'punter': 0,
             'punters': 2,
             'map': map_}
    state = State(setup)

    comm = Communicator('Alice')
