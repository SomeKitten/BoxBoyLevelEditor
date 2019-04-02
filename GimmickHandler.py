from bbmap2 import Gimmick


class GimmickHandler():
    def __init__(self, gimmicks):
        self.gimmicks = gimmicks
        self.wuids = list(gimmick.wuid for gimmick in self.gimmicks)

    def new(self, kind, x, y):
        new_wuid = max(self.wuids) + 1
        new_obj = Gimmick.new(new_wuid, kind, x, y, 1)
        self.gimmicks.append(new_obj)
        return new_obj
