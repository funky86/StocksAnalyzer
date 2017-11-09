import os

from datetime import date

cache_dir = 'cache'
conf_dir = 'conf'

cache_extensions = ('.json', '.png')

def get_cache_filename_generic(symbol, extension):
    prefix = Global.get_cache_filename_prefix()
    Global.try_create_cache_dir()
    cache_file = cache_dir + os.sep + '{}_{}{}'.format(prefix, symbol, extension)
    return cache_file

class Global:

    def try_create_cache_dir():
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def get_cache_filename_prefix():
        today = date.today()
        prefix = today.strftime('%Y-%m-%d')
        return prefix

    def get_cache_filename(symbol):
        return get_cache_filename_generic(symbol, '.json')

    def get_cache_chart_filename(symbol):
        return get_cache_filename_generic(symbol, '_chart.png')

    def clean_old_cached_files():
        Global.try_create_cache_dir()
        prefix = Global.get_cache_filename_prefix()
        count = 0
        for filename in os.listdir(cache_dir):
            if not filename.endswith(cache_extensions):
                continue
            if not filename.startswith(prefix):
                file_path = cache_dir + os.sep + filename
                os.remove(file_path)
                count += 1
        return count
