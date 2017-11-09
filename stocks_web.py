from flask import Flask
from flask import send_from_directory

from src import app_global

app = Flask(__name__)

@app.route('/')
def index():
    from src.controllers import index
    return index.get_output()

@app.route('/stocks')
def stocks():
    from src.controllers import stocks
    return stocks.get_output()

@app.route('/queries')
def queries():
    from src.controllers import queries
    return queries.get_output()

@app.route('/cache/<path:filename>')
def cache_file(filename):
    return send_from_directory(app_global.cache_dir, filename)
