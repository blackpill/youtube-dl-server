from .base import Base
class Tiktok(Base):
    def __init__(self):
        super().__init__()
        pass

    def filter_func(self, f):
        print("tiktok filter")
        flag = f['protocol'] == "https" \
            and 'width' in f \
            and f['format_note'] == "Direct video (API)" \
            and f['vcodec'] == 'h264' \
            and f['width'] <= self.max_width
        return flag    