import punterlib as P

class EagerPunter(P.PunterBase):
    def __init__(self):
        pass

    def exec_setup(self, setup):
        super(EagerPunter, self).exec_setup(setup)
        self.turn = 0

    def get_name(self):
        return 'cube_eager_punter'

    def get_move(self, prev_moves):
        for move in prev_moves:
            self.lmap.exec_move(move)
        rs = self.lmap.get_neutral_rivers()
        s, t = rs[0]
        self.turn += 1
        return {'claim': {'punter': self.punter_id, 'source': s, 'target': t}}
