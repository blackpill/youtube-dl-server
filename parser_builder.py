from site_parsers import *
from pprint import pprint
class PaserBuilder:
    def __init__(self, site_name):
        class_args = ()
        self.parser = getattr(globals()[site_name.lower()], site_name)(*class_args)

    def get_format(self, info):
        return self.parser.get_format(info)