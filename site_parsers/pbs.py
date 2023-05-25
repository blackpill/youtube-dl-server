from .base import Base
class Pbs(Base):
    def __init__(self):
        super().__init__()
        pass

    def filter_func(self, f):
        flag = f['protocol'] == "https"
        return flag
    
    def max_field(self, f):
        return f['format_id']