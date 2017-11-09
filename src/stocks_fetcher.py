import copy
import urllib.request

from bs4 import BeautifulSoup
from pathlib import Path
from shutil import copyfile

from src import app_global

google_financials = {
    'error': None,
    'company': None,
    'eps_quarterly': [],
    'eps_annual': [],
    'total_current_assets': [],
    'total_current_liabilities': [],
    'total_long_term_debt': []
}

morningstar_valuation = {
    'error': None,
    'pe_stock': None,
    'pe_stock_5y': None,
    'pe_industry': None,
    'pe_s&p': None,
    'pb_stock': None,
    'pb_stock_5y': None,
    'pb_industry': None,
    'pb_s&p': None,
    'ps_stock': None,
    'ps_stock_5y': None,
    'ps_industry': None,
    'ps_s&p': None,
    'pcf_stock': None,
    'pcf_stock_5y': None,
    'pcf_industry': None,
    'pcf_s&p': None,
    'div_stock': None,
    'div_stock_5y': None,
    'div_industry': None,
    'div_s&p': None
}

def fetch_google_values(symbol):
    url_format = 'https://finance.google.com/finance?q={0}&fstype=ii&ei=8w_aWaCqJsGGsgH29IrICQ'
    url = url_format.format(symbol)

    http_response = urllib.request.urlopen(url)
    html = http_response.read()

    soup = BeautifulSoup(html, 'html.parser')
    meta = soup.find('meta')
    tables = soup.find_all('table', id='fs-table')

    data = copy.deepcopy(google_financials)

    if len(tables) < 3:
        data['error'] = 'Error reading financials from Google Finance. Stock symbol {0} might not exist.'.format(symbol)
        return data

    description = meta['content']
    find_text = 'See revenue, expenses, profit, cash, assets, liabilities, shareholder’s equity and more for the lastest fiscal quarter/year for '
    cutoff_start = description.find(find_text)
    description = description[cutoff_start + len(find_text):]
    description = description[:description.find(' on Google Finance.')]

    income_statement_qrt = tables[0].find('tbody').find_all('tr')
    income_statement_ann = tables[1].find('tbody').find_all('tr')
    balance_sheet_qrt = tables[2].find('tbody').find_all('tr')

    data['company'] = description
    data['eps_quarterly'] = get_google_values(income_statement_qrt, 'Diluted Normalized EPS')
    data['eps_annual'] = get_google_values(income_statement_ann, 'Diluted Normalized EPS')
    data['total_current_assets'] = get_google_values(balance_sheet_qrt, 'Total Current Assets')
    data['total_current_liabilities'] = get_google_values(balance_sheet_qrt, 'Total Current Liabilities')
    data['total_long_term_debt'] = get_google_values(balance_sheet_qrt, 'Total Long Term Debt')

    return data

def fetch_morningstar_values(symbol):
    url_format = 'https://financials.morningstar.com/valuate/current-valuation-list.action?&t={0}&region=usa&culture=en-US'
    url = url_format.format(symbol)

    http_response = urllib.request.urlopen(url)
    html = http_response.read()

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='currentValuationTable')

    data = copy.deepcopy(morningstar_valuation)

    if not table:
        data['error'] = 'Error reading valuation from Morningstar. Stock symbol {0} might not exist.'.format(symbol)
        return data

    table = table.find('tbody').find_all('tr')

    row_idx = 0
    for row in table:
        cells = row.find_all('td')
        col_idx = 0
        for cell in cells:
            value = None
            try:
                value = float(cell.string.replace(',', ''))
            except:
                pass

            if row_idx == 1:
                if col_idx == 0:
                    data['pe_stock'] = value
                elif col_idx == 1:
                    data['pe_industry'] = value
                elif col_idx == 2:
                    data['pe_s&p'] = value
                elif col_idx == 3:
                    data['pe_stock_5y'] = value
            elif row_idx == 3:
                if col_idx == 0:
                    data['pb_stock'] = value
                elif col_idx == 1:
                    data['pb_industry'] = value
                elif col_idx == 2:
                    data['pb_s&p'] = value
                elif col_idx == 3:
                    data['pb_stock_5y'] = value
            elif row_idx == 5:
                if col_idx == 0:
                    data['ps_stock'] = value
                elif col_idx == 1:
                    data['ps_industry'] = value
                elif col_idx == 2:
                    data['ps_s&p'] = value
                elif col_idx == 3:
                    data['ps_stock_5y'] = value
            elif row_idx == 7:
                if col_idx == 0:
                    data['pcf_stock'] = value
                elif col_idx == 1:
                    data['pcf_industry'] = value
                elif col_idx == 2:
                    data['pcf_s&p'] = value
                elif col_idx == 3:
                    data['pcf_stock_5y'] = value
            elif row_idx == 9:
                if col_idx == 0:
                    data['div_stock'] = value
                elif col_idx == 1:
                    data['div_industry'] = value
                elif col_idx == 2:
                    data['div_s&p'] = value
                elif col_idx == 3:
                    data['div_stock_5y'] = value

            col_idx += 1

        row_idx += 1

    return data

def get_google_values(table, search_string):
    data = []
    found = False
    for row in table:
        cells = row.find_all('td')
        for cell in cells:
            if not cell.string:
                continue
            if found:
                value = None
                try:
                    value = float(cell.string.replace(',', ''))
                except:
                    pass
                finally:
                    data.append(value)
                continue
            if cell.string.startswith(search_string):
                found = True
        if found:
            break
    return data

class StocksURLOpener(urllib.request.FancyURLopener):
    version = 'Mozilla/5.0'

url_opener = StocksURLOpener()

def fetch_chart(symbol):
    url_format = 'http://stockcharts.com/c-sc/sc?s={}&p=W&yr=10&mn=0&dy=0&i=p96700093712&r=1509991452925'
    url = url_format.format(symbol)

    response = url_opener.retrieve(url)
    tmp_path = response[0]

    tmp_file = Path(tmp_path)

    if tmp_file.is_file():
        permanent_path = app_global.Global.get_cache_chart_filename(symbol)
        copyfile(tmp_path, permanent_path)
        return permanent_path
    else:
        return ''
