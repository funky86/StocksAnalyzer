from flask import render_template
from flask import request

def get_output():
    data = []
    error = []

    request_type = request.args.get('request_type')
    for_cache = request.args.get('for_cache')

    if request_type is None:
        error.append("Missing expected HTTP parameter: request_type")
    else:
        if request_type == 'symbols':
            fill_stocks_data_symbols(data, error)
        elif request_type == 'finviz':
            fill_stocks_data_finviz(data, error)

        prepare_for_output(data)

    if for_cache is None:
        return render_template('stocks.html', stocks_data=data, error=error)
    else:
        return 'data_length={0} error={1}'.format(len(data), error)

def fill_stocks_data_symbols(data, error):
    from src import stocks

    symbols = request.args.get('list')

    if symbols is None:
        error.append("Missing expected HTTP parameter: list")
        return

    for symbol in symbols.rsplit(','):
        stock_data = stocks.get_values(symbol)
        data.append(stock_data)

def fill_stocks_data_finviz(data, error):
    from bs4 import BeautifulSoup
    import urllib.request
    
    from src import stocks

    url = request.args.get('url')

    if url is None:
        error.append("Missing expected HTTP parameter: url")
        return
    expected_url = "https://finviz.com/screener.ashx"
    if not url.startswith(expected_url):
        error.append("The URL doesn't start with expected value: {0}".format(expected_url))
        return

    http_response = urllib.request.urlopen(url)
    html = http_response.read()

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', width="100%", cellpadding="10", cellspacing="0", border="0")
    spans = table.find('tr').find('td').find_all('span')

    for span in spans:
        if span.b:
            symbol = span.b.string
        else:
            symbol = span.string

        if not symbol:
            continue
        symbol = symbol.strip()

        stock_data = stocks.get_values(symbol)
        data.append(stock_data)

def prepare_for_output(data):
    round_digits = 1
    for symbol_data in data:
        process_dictionary(symbol_data, 'financials', round_digits)
        process_dictionary(symbol_data, 'valuation', round_digits)

def process_dictionary(symbol_data, root_key, round_digits):
    for key in symbol_data[root_key]:
            value = symbol_data[root_key][key]

            if isinstance(value, list):

                for i in range(0, len(value)):
                    value_tmp = value[i]

                    if isinstance(value_tmp, float):
                        value_tmp = round(value_tmp, round_digits)
                    elif value_tmp is None:
                        value_tmp = ''

                    symbol_data[root_key][key][i] = value_tmp
            else:

                if isinstance(value, float):
                    value = round(value, round_digits)
                elif value is None:
                    value = ''

                symbol_data[root_key][key] = value
