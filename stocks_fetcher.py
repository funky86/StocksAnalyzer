from bs4 import BeautifulSoup

import urllib.request

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

    if len(tables) != 6:
        google_financials['error'] = 'Error reading financials from Google Finance. Stock symbol {0} might not exist.'.format(symbol)
        return google_financials

    description = meta['content']
    find_text = 'See revenue, expenses, profit, cash, assets, liabilities, shareholder’s equity and more for the lastest fiscal quarter/year for '
    cutoff_start = description.find(find_text)
    description = description[cutoff_start + len(find_text):]
    description = description[:description.find(' on Google Finance.')]

    income_statement_qrt = tables[0].find('tbody').find_all('tr')
    income_statement_ann = tables[1].find('tbody').find_all('tr')
    balance_sheet_qrt = tables[2].find('tbody').find_all('tr')

    google_financials['company'] = description
    google_financials['eps_quarterly'] = get_google_values(income_statement_qrt, 'Diluted Normalized EPS')
    google_financials['eps_annual'] = get_google_values(income_statement_ann, 'Diluted Normalized EPS')
    google_financials['total_current_assets'] = get_google_values(balance_sheet_qrt, 'Total Current Assets')
    google_financials['total_current_liabilities'] = get_google_values(balance_sheet_qrt, 'Total Current Liabilities')
    google_financials['total_long_term_debt'] = get_google_values(balance_sheet_qrt, 'Total Long Term Debt')

    return google_financials

def fetch_morningstar_values(symbol):
    url_format = 'https://financials.morningstar.com/valuate/current-valuation-list.action?&t={0}&region=usa&culture=en-US'
    url = url_format.format(symbol)

    http_response = urllib.request.urlopen(url)
    html = http_response.read()

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='currentValuationTable')

    if not table:
        morningstar_valuation['error'] = 'Error reading valuation from Morningstar. Stock symbol {0} might not exist.'.format(symbol)
        return morningstar_valuation

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
                    morningstar_valuation['pe_stock'] = value
                elif col_idx == 1:
                    morningstar_valuation['pe_industry'] = value
                elif col_idx == 2:
                    morningstar_valuation['pe_s&p'] = value
                elif col_idx == 3:
                    morningstar_valuation['pe_stock_5y'] = value
            elif row_idx == 3:
                if col_idx == 0:
                    morningstar_valuation['pb_stock'] = value
                elif col_idx == 1:
                    morningstar_valuation['pb_industry'] = value
                elif col_idx == 2:
                    morningstar_valuation['pb_s&p'] = value
                elif col_idx == 3:
                    morningstar_valuation['pb_stock_5y'] = value
            elif row_idx == 9:
                if col_idx == 0:
                    morningstar_valuation['div_stock'] = value
                elif col_idx == 1:
                    morningstar_valuation['div_industry'] = value
                elif col_idx == 2:
                    morningstar_valuation['div_s&p'] = value
                elif col_idx == 3:
                    morningstar_valuation['div_stock_5y'] = value

            col_idx += 1

        row_idx += 1

    return morningstar_valuation

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

