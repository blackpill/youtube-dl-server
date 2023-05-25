from .base import Base
class Espn(Base):
    def __init__(self):
        super().__init__()
        pass

    def filter_func(self, f):
        flag = f['protocol'] == "https" and 'width' in f
        return flag