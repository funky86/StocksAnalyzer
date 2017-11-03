import os

from datetime import date

cache_dir = 'cache'
conf_dir = 'conf'

class Global:

    def try_create_cache_dir():
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def get_cache_filename_prefix():
        today = date.today()
        prefix = today.strftime('%Y-%m-%d')
        return prefix

    def get_cache_filename(symbol):
        prefix = Global.get_cache_filename_prefix()

        Global.try_create_cache_dir()

        cache_file = cache_dir + os.sep + '{0}_{1}.json'.format(prefix, symbol)

        return cache_file

    def clean_old_cached_files():
        Global.try_create_cache_dir()
        prefix = Global.get_cache_filename_prefix()
        count = 0
        for filename in os.listdir(cache_dir):
            if not filename.endswith('.json'):
                continue
            if not filename.startswith(prefix):
                file_path = cache_dir + os.sep + filename
                os.remove(file_path)
                count += 1
        return count
