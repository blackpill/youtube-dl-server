from .base import Base
class Cbc(Base):
    def __init__(self):
        super().__init__()
        pass

    def filter_func(self, f):
        flag = f['protocol'] == "https"
        return flag