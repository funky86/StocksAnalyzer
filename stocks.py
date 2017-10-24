import math
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
    data['financials']['eps_quarterly_pace'] = None

    data['valuation']['pe'] = None
    data['valuation']['pb'] = None
    data['valuation']['ps'] = None
    data['valuation']['pcf'] = None
    
    data['evaluation'] = {}
    data['evaluation']['current_ratio'] = None
    data['evaluation']['debt_ratio'] = None
    data['evaluation']['eps_annual_positive'] = None
    data['evaluation']['eps_quarterly_pace'] = None
    data['evaluation']['div_stock'] = None
    data['evaluation']['pe'] = None
    data['evaluation']['pb'] = None
    data['evaluation']['ps'] = None
    data['evaluation']['pcf'] = None

    if data['error']:
        return data

    calculate_ratios(data)
    calculate_eps_growth(data, 'eps_quarterly', 'eps_quarterly_growth', 'eps_quarterly_positive')
    calculate_eps_growth(data, 'eps_annual', 'eps_annual_growth', 'eps_annual_positive')
    calculate_eps_pace(data, 'eps_quarterly', 'eps_quarterly_pace')
    calculate_average(data, 'pe', 'pe_stock', ['pe_stock_5y', 'pe_industry', 'pe_s&p'])
    calculate_average(data, 'pb', 'pb_stock', ['pb_stock_5y', 'pb_industry', 'pb_s&p'])
    calculate_average(data, 'ps', 'ps_stock', ['ps_stock_5y', 'ps_industry', 'ps_s&p'])
    calculate_average(data, 'pcf', 'pcf_stock', ['pcf_stock_5y', 'pcf_industry', 'pcf_s&p'])
    evaluate_values(data)

    return data

def fetch_data(symbol):
    today = date.today()
    date_str = today.strftime('%Y-%m-%d')
    cache_file = '{0}_{1}.json'.format(date_str, symbol)

    data = {
        'error': None,
        'financials': {},
        'valuation': {},
        'evaluation': {}
    }

    if os.path.exists(cache_file):
        data = json.load(open(cache_file))
    else:
        financials = stocks_fetcher.fetch_google_values(symbol)
        valuation = stocks_fetcher.fetch_morningstar_values(symbol)

        if financials['error'] is not None:
            data['error'] = financials['error']
        elif valuation['error'] is not None:
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
    try:
        data['financials'][key_positive] = positive / count * 100
    except:
        pass

def calculate_average(data, key_result, key_value, key_checks):
    value = data['valuation'][key_value]

    try:
        avg = 0
        for key_check in key_checks:
            check = data['valuation'][key_check]
            avg += (check - value) / check * -100
        avg = avg / len(key_checks)
        data['valuation'][key_result] = avg
    except:
        pass

def calculate_eps_pace(data, key_value, key_pace):
    try:
        eps = data['financials'][key_value]
        count = math.ceil(len(eps) / 2)
        is_odd = len(eps) % 2 == 1
        avg1 = 0
        avg2 = 0
        for i in range(len(eps)):
            curr = eps[i]
            if is_odd:
                if i < count-1:
                    avg1 += curr
                elif i >= count:
                    avg2 += curr
                else:
                    avg1 += curr
                    avg2 += curr
            else:
                if i <= count-1:
                    avg1 += curr
                else:
                    avg2 += curr
        avg1 = avg1 / count
        avg2 = avg2 / count
        data['financials'][key_pace] = (avg2 - avg1) / avg1 * 100
    except:
        pass

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
        data['evaluation']['eps_quarterly_pace'] = data['financials']['eps_quarterly_pace'] > 0
    except:
        pass

    try:
        data['evaluation']['div_stock'] = data['valuation']['div_stock'] > 0
    except:
        data['evaluation']['div_stock'] = False
        pass

    try:
        data['evaluation']['pe'] = data['valuation']['pe'] < 0
    except:
        pass

    try:
        data['evaluation']['pb'] = data['valuation']['pb'] < 0
    except:
        pass

    try:
        data['evaluation']['ps'] = data['valuation']['ps'] < 0
    except:
        pass

    try:
        data['evaluation']['pcf'] = data['valuation']['pcf'] < 0
    except:
        pass
