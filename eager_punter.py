#!/usr/bin/env python
import json
import sys
import punterlib as P

class EagerPunter(P.PunterBase):
    def __init__(self):
        pass

    def exec_setup(self, setup):
        super(EagerPunter, self).exec_setup(setup)
        ret = {'ready': self.punter_id, 'state': self.dump_state()}
        return ret

    def get_name(self):
        return 'cube_eager_punter'

    def recover_state(self, state):
        self.punter_id = state['punter_id']
        self.num_punters = state['num_punters']
        self.lmap = P.recover_listmap(state['lmap'])

    def dump_state(self):
        ret = {'punter_id': self.punter_id,
               'num_punters': self.num_punters,
               'lmap': self.lmap.dump()}
        return ret

    def get_move(self, prev_moves):
        for move in prev_moves:
            self.lmap.exec_move(move)
        rs = self.lmap.get_neutral_rivers()
        s, t = rs[0]
        return {'claim': {'punter': self.punter_id, 'source': s, 'target': t}}

if __name__ == '__main__':
    punter = EagerPunter()
    punter.exec_all()
