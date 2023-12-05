from site_parsers import *
from pprint import pprint
class PaserBuilder:
    def __init__(self, site_name):
        class_args = ()
        self.parser = getattr(globals()[site_name.lower()], site_name)(*class_args)

    def get_best_format(self, info):
        return self.parser.get_best_format(info)
    
    def get_best_audio(self, info):
        return self.parser.get_best_audio(info)
    
    def get_all_formats(self, info):
        return self.parser.get_all_formats(info)
    
    def get_all_streams(self, info):
        return self.parser.get_all_streams(info)