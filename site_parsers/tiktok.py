from .base_parser import BaseParser
class Tiktok(BaseParser):
    def __init__(self):
        super().__init__()
        pass

    def filter_func(self, f):
        flag = f['protocol'] == "https" \
           and f['width'] is not None \
           and f['format_note'] == "Direct video (API)" \
           and f['vcodec'] == 'h264' \
           and f['width'] <= 1280 
        return flag    