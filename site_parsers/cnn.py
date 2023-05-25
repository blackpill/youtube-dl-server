from .base import Base
class Cnn(Base):
    def __init__(self):
        super().__init__()
        pass

    def filter_func(self, f):
        flag = f['protocol'] == "https"
        return flag
