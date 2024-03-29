import argparse
import json
import subprocess
import sys

import punterlib as P
from eager_punter import EagerPunter
from bfs_punter import BFSPunter

TIMEOUT_SETUP = 1
TIMEOUT_GAMEPLAY = 1

def send_handshake(punter):
    recv = P.recv_in_json(punter)
    assert('me' in recv)
    send = {'you': recv['me']}
    P.send_in_json(punter, send)

def send_setup(punter, punter_id, setup):
    send_handshake(punter)
    P.send_in_json(punter, setup)
    recv = P.recv_in_json(punter)
    assert(recv['ready'] == punter_id)
    return recv['state']

def send_gameplay(punter, moves, prev_state):
    send_handshake(punter)
    game = {'move': {'moves': moves}, 'state': prev_state}
    P.send_in_json(punter, game)
    result = {}
    def process_recv(recv):
        if 'claim' in recv or 'pass' in recv:
            result['move'] = recv
        elif 'state' in recv:
            result['next_state'] = recv['state']
        else:
            assert(False)  # Not move nor state.
    process_recv(P.recv_in_json(punter))
    process_recv(P.recv_in_json(punter))
    return result['move'], result['next_state']

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('map_path',
                           action='store',
                           type=str,
                           metavar='MAP')
    argparser.add_argument('punter_cmds',
                           action='store',
                           type=str,
                           nargs='+',
                           metavar='PUNTER')
    argparser.add_argument('-l',
                           dest='map_log_path',
                           action='store',
                           type=str,
                           default='map.log',
                           metavar='LOG')
    args = argparser.parse_args()

    with open(args.map_path) as fp:
        map_ = json.load(fp)
    # Init global info.
    print('punters:', args.punter_cmds, file=sys.stderr)
    num_punters = len(args.punter_cmds)
    setup = {'punter': None,
             'punters': num_punters,
             'map': map_}
    lmap = P.ListMap()
    lmap.exec_setup(setup)
    map_log = [lmap.dump()]
    last_moves = []
    for p in range(num_punters):
        last_moves.append({'pass': {'punter': p}})
    # Setup punters.
    states = [None] * num_punters
    for punter_id, cmd in enumerate(args.punter_cmds):
        punter = subprocess.Popen(cmd,
                                  shell=True,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)
        setup['punter'] = punter_id
        state = send_setup(punter, punter_id, setup)
        states[punter_id] = state
    print('[INFO] initial states:', states, file=sys.stderr)

    for turn in range(lmap.num_rivers()):
        punter_id = turn % num_punters
        cmd = args.punter_cmds[punter_id]
        punter = subprocess.Popen(cmd,
                                  shell=True,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)
        move, state = send_gameplay(punter, last_moves, states[punter_id])
        print('[INFO] turn, punter_id, move, state:', turn, punter_id, move, state, file=sys.stderr)
        last_moves[punter_id] = move
        states[punter_id] = state
        print('[INFO] move', move, file=sys.stderr)
        lmap.exec_move(move)
        map_log.append(lmap.dump())

    print('[INFO] punter_to_score:', lmap.get_punter_to_score(), file=sys.stderr)
    print('[INFO] output map log', file=sys.stderr)
    with open('map.log', 'w') as fp:
        json.dump(map_log, fp, indent=2)
