from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route('/')
def index():
    return 'Stocks Analyzer'

@app.route('/stocks')
def stocks():
    import stocks
    symbols = request.args.get('symbols')
    data = []
    if symbols:
	    for symbol in symbols.rsplit(','):
	        stock_data = stocks.get_values(symbol)
	        data.append(stock_data)
    return render_template('stocks.html', stocks_data=data)

@app.route('/queries')
def queries():
	return render_template('queries.html')
