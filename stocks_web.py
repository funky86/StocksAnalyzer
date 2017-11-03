from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route('/')
def index():
    return 'Stocks Analyzer'

@app.route('/stocks')
def stocks():
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

    if for_cache is None:
        return render_template('stocks.html', stocks_data=data, error=error)
    else:
        return 'data_length={0} error={1}'.format(len(data), error)

@app.route('/queries')
def queries():
    return render_template('queries.html')

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
    tables = soup.find_all('table')
    spans = tables[12].find('tr').find('td').find_all('span')

    for span in spans:
        symbol = span.b.string

        if not symbol:
            continue
        symbol = symbol.strip()

        stock_data = stocks.get_values(symbol)
        data.append(stock_data)

