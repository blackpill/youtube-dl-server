from pprint import pprint
class BaseParser:
    def __init__(self):
        pass

    def filter_func(self, f):
        flag = f['protocol'] == "https" \
           and f['width'] is not None \
           and f['width'] <= 1280 
        return flag
    
    def max_field(self, f):
        return f['width']
    
    def get_format(self, info):
        formats = info['formats']
        filtered_formats = filter(self.filter_func, formats)        
        result = max(filtered_formats, key=self.max_field)
        result['error'] = None
        return result
