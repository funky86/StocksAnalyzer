import urllib.request

def fetch_yahoo_values(symbols):
    """
    Yahoo Finance API query parameters:
    s Symbol
    m6 Percent Change From 200 Day Moving Average
    m8 Percent Change From 50 Day Moving Average
    j6 Percent Change From 52 week Low
    k5 Percent Change From 52 week High
    v Volume
    a2 Average Daily Volume
    """

    symbols_str = '+'.join(symbols)

    url_format = 'https://finance.yahoo.com/d/quotes.csv?s={0}&f=sm6m8j6k5va2'
    url = url_format.format(symbols_str)
    print(url)
    http_response = urllib.request.urlopen(url)
    html = http_response.read()

    print(html)

symbols = ['MSFT','GOOGL']
fetch_yahoo_values(symbols)
