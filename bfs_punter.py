#!/usr/bin/env python
import copy
import json
import sys

import punterlib as P

class MoveTree():
    def __init__(self, move, is_mine):
        self.move = move  # root => None.
        self.is_mine = is_mine
        self.leafs = []

    def set_evaluation(self, leaf_id, ev):
        self.selected_leaf_id = leaf_id
        self.evaluation = ev

    def get_evaluation(self):
        return self.evaluation

    def add_leaf(self, l):
        self.leafs.append(l)

    def evaluate_leafs(self):
        if self.leafs == []:
            assert(self.evaluation is not None)
        else:
            for l in self.leafs:
                l.evaluate_leafs()
            evs = map(lambda l: l.get_evaluation(), self.leafs)
            if self.is_mine:
                leaf_id, ev = max(enumerate(evs), key=lambda ev: ev[1])
            else:
                leaf_id, ev = min(enumerate(evs), key=lambda ev: ev[1])
            self.set_evaluation(leaf_id, ev)

    def get_max_evaluation_move(self):
        return self.leafs[self.selected_leaf_id].move


class BFSPunter(P.PunterBase):
    def __init__(self):
        pass

    def exec_setup(self, setup):
        super(BFSPunter, self).exec_setup(setup)
        return {'ready': self.punter_id, 'state': self.dump_state()}

    def get_name(self):
        return 'cube_punter_0'

    def recover_state(self, state):
        self.punter_id = state['punter_id']
        self.num_punters = state['num_punters']
        self.lmap = P.recover_listmap(state['lmap'])

    def dump_state(self):
        return {'punter_id': self.punter_id,
                'num_punters': self.num_punters,
                'lmap': self.lmap.dump()}

    def evaluate_punter_to_score(self, p2s):
        my_score = p2s[self.punter_id]
        max_enemy_score = max([s for p, s in enumerate(p2s) if p != self.punter_id])
        return my_score - max_enemy_score

    def bfs(self, max_depth=2):
        def bfs_aux(lmap, active_punter, move_tree, depth):
            if depth >= max_depth:
                e = self.evaluate_punter_to_score(lmap.get_punter_to_score())
                move_tree.set_evaluation(None, e)
                return
            rivers = lmap.get_neutral_rivers()
            moves = list(map(lambda r: {'claim': {'punter': active_punter,
                                                  'source': r[0],
                                                  'target': r[1]}},
                             rivers))
            moves.append({'pass': {'punter': active_punter}})
            for move in moves:
                lmap_copy = copy.deepcopy(lmap)
                lmap_copy.exec_move(move)
                next_active_punter = (active_punter + 1) % self.num_punters
                leaf = MoveTree(move, next_active_punter == self.punter_id)
                bfs_aux(lmap_copy, next_active_punter, leaf, depth + 1)
                move_tree.add_leaf(leaf)
        #with open('x.log', 'w') as fp:
        move_tree_root = MoveTree(None, True)
        bfs_aux(self.lmap, self.punter_id, move_tree_root, 0)
        move_tree_root.evaluate_leafs()
        return move_tree_root.get_max_evaluation_move()


    def get_move(self, prev_moves):
        for move in prev_moves:
            self.lmap.exec_move(move)
        return self.bfs()

if __name__ == '__main__':
    punter = BFSPunter()
    punter.exec_all()
