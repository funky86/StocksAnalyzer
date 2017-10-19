import json
import os
import stocks_fetcher

from datetime import date

def get_values(symbol):
    data = fetch_data(symbol)

    data['financials']['net_current_assets'] = []
    data['financials']['current_ratio'] = []
    data['financials']['debt_ratio'] = []
    data['financials']['eps_quarterly_growth'] = []
    data['financials']['eps_quarterly_positive'] = None
    data['financials']['eps_annual_growth'] = []
    data['financials']['eps_annual_positive'] = None
    data['evaluation'] = {
        'current_ratio': None,
        'debt_ratio': None,
        'eps_annual_positive': None,
        'div_stock': None
    }

    if data['error']:
        return data

    calculate_ratios(data)
    calculate_eps_growth(data, 'eps_quarterly', 'eps_quarterly_growth', 'eps_quarterly_positive')
    calculate_eps_growth(data, 'eps_annual', 'eps_annual_growth', 'eps_annual_positive')
    evaluate_values(data)

    return data

def fetch_data(symbol):
    today = date.today()
    date_str = today.strftime('%Y-%m-%d')
    cache_file = '{0}_{1}.json'.format(date_str, symbol)

    data = {
        'error': None,
        'financials': None,
        'valuation': None,
        'evaluation': None
    }

    if os.path.exists(cache_file):
        data = json.load(open(cache_file))
    else:
        financials = stocks_fetcher.fetch_google_values(symbol)
        valuation = stocks_fetcher.fetch_morningstar_values(symbol)

        if financials['error']:
            data['error'] = financials['error']
        elif valuation['error']:
            data['error'] = valuation['error']
        else:
            data['financials'] = financials
            data['valuation'] = valuation

        with open(cache_file, 'w') as file:
            file.write(json.dumps(data))

    return data

def calculate_ratios(data):
    total_current_assets = data['financials']['total_current_assets']
    total_current_liabilities = data['financials']['total_current_liabilities']
    total_long_term_debt = data['financials']['total_long_term_debt']

    for assets, liabilities, debt in zip(total_current_assets, total_current_liabilities, total_long_term_debt):
        net_assets = None
        try:
            net_assets = assets - liabilities
        except:
            pass
        finally:
            data['financials']['net_current_assets'].append(net_assets)

        current_ratio = None
        try:
            current_ratio = assets / liabilities
        except:
            pass
        finally:
            data['financials']['current_ratio'].append(current_ratio)

        debt_ratio = None
        try:
            debt_ratio = debt / net_assets
        except:
            pass
        finally:
            data['financials']['debt_ratio'].append(debt_ratio)

def calculate_eps_growth(data, key_value, key_growth, key_positive):
    eps = data['financials'][key_value]

    count = len(eps) - 1
    positive = 0
    for i in range(count):
        curr = eps[i]
        prev = eps[i+1]

        value = None
        try:
            value = (curr - prev) / prev * 100
            if value > 0:
                positive += 1
        except:
            pass
        finally:
            data['financials'][key_growth].append(value)
    data['financials'][key_positive] = positive / count * 100

def evaluate_values(data):
    for current_ratio, debt_ratio in zip(data['financials']['current_ratio'], data['financials']['debt_ratio']):
        try:
            data['evaluation']['current_ratio'] = current_ratio >= 1.5
        except:
            pass

        try:
            data['evaluation']['debt_ratio'] = debt_ratio <= 1.1
        except:
            pass

    try:
        data['evaluation']['eps_annual_positive'] = data['financials']['eps_annual_positive'] == 100
    except:
        pass

    try:
        data['evaluation']['div_stock'] = data['valuation']['div_stock'] > 0
    except:
        data['evaluation']['div_stock'] = False
        pass
