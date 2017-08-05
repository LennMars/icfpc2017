#!/usr/bin/env python
import copy
import json
import sys

import punterlib as P

# Implementation of MinMax method.
class MoveTree():
    def __init__(self, move, is_mine):
        self.move = move  # root => None.
        self.is_mine = is_mine
        self.children = []  # leaf => Empty.

    def set_evaluation(self, child_id, ev):
        # The index of the child which achieves min/max evaluation.
        self.selected_child_id = child_id
        self.evaluation = ev

    def get_evaluation(self):
        return self.evaluation

    def add_child(self, l):
        self.children.append(l)

    def evaluate_children(self):
        if self.children == []:
            # Leaf node must be already evaluated.
            assert(self.evaluation is not None)
        else:
            for l in self.children:
                l.evaluate_children()
            evs = map(lambda l: l.get_evaluation(), self.children)
            # MinMax method:
            # If the current node is my turn,
            # the move with the highest evaluation should be selected,
            # and vice versa.
            if self.is_mine:
                child_id, ev = max(enumerate(evs), key=lambda ev: ev[1])
            else:
                child_id, ev = min(enumerate(evs), key=lambda ev: ev[1])
            self.set_evaluation(child_id, ev)

    def get_max_evaluation_move(self):
        return self.children[self.selected_child_id].move


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

    # Evaluate list of all punters' scores.
    def evaluate_punter_to_score(self, p2s):
        my_score = p2s[self.punter_id]
        max_enemy_score = max([s for p, s in enumerate(p2s) if p != self.punter_id])
        return my_score - max_enemy_score

    # Forward path of MinMax method.
    def bfs(self, max_depth=2):
        def bfs_aux(lmap, active_punter, move_tree, depth):
            if depth >= max_depth:
                e = self.evaluate_punter_to_score(lmap.get_punter_to_score())
                move_tree.set_evaluation(None, e)
                return
            # Generate possible moves.
            rivers = lmap.get_neutral_rivers()
            moves = list(map(lambda r: {'claim': {'punter': active_punter,
                                                  'source': r[0],
                                                  'target': r[1]}},
                             rivers))
            moves.append({'pass': {'punter': active_punter}})
            # Execute each move and recurrently evaluate child nodes.
            for move in moves:
                lmap_copy = copy.deepcopy(lmap)
                lmap_copy.exec_move(move)
                next_active_punter = (active_punter + 1) % self.num_punters
                child = MoveTree(move, next_active_punter == self.punter_id)
                bfs_aux(lmap_copy, next_active_punter, child, depth + 1)
                move_tree.add_child(child)
        move_tree_root = MoveTree(None, True)
        bfs_aux(self.lmap, self.punter_id, move_tree_root, 0)
        move_tree_root.evaluate_children()
        return move_tree_root.get_max_evaluation_move()

    def get_move(self, prev_moves):
        for move in prev_moves:
            self.lmap.exec_move(move)
        return self.bfs()

if __name__ == '__main__':
    punter = BFSPunter()
    punter.exec_all()
