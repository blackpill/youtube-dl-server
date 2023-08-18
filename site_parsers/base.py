from pprint import pprint
class Base:
    def __init__(self):
        self.max_width = 1280
        pass

    # set the criteria which formats can be played
    def filter_func(self, f):
        print('base filter')
        flag = f['protocol'] == "https" \
           and 'width' in f \
           and f['width'] \
           and f['width'] <= self.max_width
        return flag
    
    # set the field, which is used to choose the best resolution
    def max_field(self, f):
        return f['width']
    
    def get_best_format(self, info):
        formats = info['formats']
        try:
            filtered_formats = filter(self.filter_func, formats)
        except Exception as e:
            pprint(e)
        result = max(filtered_formats, key=self.max_field)        
        result['error'] = None
        return result
    
    def get_all_formats(self, info):
        formats = info['formats']
        result = {
            "formats": formats,
            "error": None
        }
        return result
