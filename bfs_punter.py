import copy

import punterlib as P

class BFSPunter(P.PunterBase):
    def __init__(self):
        pass

    def exec_setup(self, setup):
        super(BFSPunter, self).exec_setup(setup)
        self.turn = 0

    def get_name(self):
        return 'cube_punter_0'

    def bfs(self, max_depth=2):
        def bfs_aux(lmap, active_punter, moves, depth):
            if depth >= max_depth:
                return moves, lmap.get_punter_to_score()
            acc = []
            rivers = lmap.get_neutral_rivers()
            for s, t in rivers:
                lmap_copy = copy.deepcopy(lmap)
                move = {'claim': {'punter': active_punter,
                                  'source': s,
                                  'target': t}}
                lmap_copy.exec_move(move)
                next_active_punter = (active_punter + 1) % self.num_punters
                acc.append(bfs_aux(lmap_copy, next_active_punter, moves + [move], depth + 1))
            return acc
        print('[INFO]', bfs_aux(self.lmap, self.punter_id, [], 0))

    def get_move(self, prev_moves):
        for move in prev_moves:
            self.lmap.exec_move(move)
        self.bfs()
        self.turn += 1
        return {'pass': {'punter': self.punter_id}}
