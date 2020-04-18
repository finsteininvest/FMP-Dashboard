from app import app
from flask import render_template, request
import pandas as pd
from app import fmp
import html


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='FMP Dashboard')

@app.route('/search', methods=['POST'])
def search():
	searchstring = request.form['searchstring']
	searchstring = html.escape(searchstring)
	if 'select' in searchstring:
		searchstring = ''
	if 'update' in searchstring:
		searchstring = ''
	if ';' in searchstring:
		searchstring = ''
	if '--' in searchstring:
		searchstring = ''
	if '%' in searchstring:
		searchstring = ''
	available_stocks = fmp.get_symbols_list()
	available_stocks = available_stocks.dropna()
	found_stocks_name = available_stocks[available_stocks['name'].str.contains(searchstring)]
	found_stocks_symbol = available_stocks[available_stocks.index.str.contains(searchstring)]
	found_symbols = pd.concat([found_stocks_name, found_stocks_symbol])
	return render_template('stock_list.html', title='FMP Dashboard', found_symbols = found_symbols)

@app.route('/symbol/<symbol>')
def symbol(symbol):
	searchsymbol = html.escape(symbol)
	available_stocks = fmp.get_symbols_list()
	validsymbol = available_stocks[available_stocks.index.str.contains(searchsymbol)]

	if len(validsymbol)>0:
		eps = fmp.get_historic_eps(searchsymbol)
		eps['year'] = eps.index.str[:4]
		roe = fmp.get_historic_roe(searchsymbol)
		roe['year'] = roe.index.str[:4]
		# Some companies do not pay dividends
		try:
			dividends = fmp.get_historic_dividend(searchsymbol)
			dividends['year_str'] = dividends.index.format()
			dividends['year'] = dividends['year_str'].str[:4]
		except:
			year_list = []
			for year in eps['year']:
				year_list.append([year,0])
			dividends = pd.DataFrame(year_list, columns = ['year','adjDividend'])
		book_value_per_share = fmp.get_book_value_per_share(searchsymbol)
		book_value_per_share['year'] = book_value_per_share.index.str[:4]
		
		current_ratio_tmp = fmp.get_current_ratio(searchsymbol)
		current_ratio_tmp['year'] = current_ratio_tmp.index.str[:4]
		current_ratio = current_ratio_tmp[['year', 'current_ratio']]

		debt_equity_tmp = fmp.get_debt_equity(searchsymbol)
		debt_equity_tmp['year'] = debt_equity_tmp.index.str[:4]
		debt_equity = debt_equity_tmp[['year', 'de_ratio']]


		all_data = pd.merge(eps, roe, on='year')
		all_data = pd.merge(all_data, dividends, on='year')
		all_data = pd.merge(all_data, book_value_per_share, on='year')
		all_data = pd.merge(all_data, current_ratio, on='year')
		all_data = pd.merge(all_data, debt_equity, on='year')

		price_earning_ratio = fmp.get_price_earning_ratio(searchsymbol)
		price_earning_ratio = f'{price_earning_ratio:.2f}'
		price_book_ratio = fmp.get_price_book_ratio(searchsymbol)
		price_book_ratio = f'{price_book_ratio:.2f}'

		historic_values = fmp.get_historic_values(searchsymbol, type = '')
		historic_values = historic_values[-500:]
		legend = f'Close price {searchsymbol}'
		labels = historic_values.index.values.tolist()
		values = historic_values['close'].values.tolist()

		return render_template('symbol_details.html', 
								title='FMP Dashboard', 
								data = all_data, 
								company_name = validsymbol['name'].iloc[0], 
								values=values, 
								labels=labels, 
								legend=legend,
								price_earning_ratio = price_earning_ratio,
								price_book_ratio = price_book_ratio)
 
	else:
		return render_template('index.html', title='FMP Dashboard')
