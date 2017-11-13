import logging
import logging.config
import os
import time
import urllib.request
import urllib.parse

import app_global

url_format = 'http://127.0.0.1:80/stocks?request_type=finviz&for_cache&url={0}'
finviz_urls = [
    'https://finviz.com/screener.ashx?v=410&s=ta_unusualvolume&ft=3',
    'https://finviz.com/screener.ashx?v=410&f=fa_eps5years_o25,ta_perf_1wup,ta_perf2_dup&ft=4']


def main():
    clean_old_cached_files()
    
    for finviz_url in finviz_urls:
        make_http_request(finviz_url)

def clean_old_cached_files():
    count = app_global.Global.clean_old_cached_files()
    logger.info('Cache cleared: files count={0}'.format(count))

def make_http_request(finviz_url):
    logger.info('Caching started ...')

    start_time = time.time()

    finviz_url_escaped = urllib.parse.quote(finviz_url)
    url = url_format.format(finviz_url_escaped)

    http_response = urllib.request.urlopen(url)
    response = http_response.read()

    duration_time = time.time() - start_time

    logger.info('Cached: {0} duration={1}s finviz_url={2}'.format(response, round(duration_time, 3), finviz_url))

if __name__ == '__main__':
    logging.config.fileConfig(app_global.conf_dir + os.sep + 'logging.conf')
    logger = logging.getLogger(os.path.basename(__file__))
    main()
