from fiab.base.well import BaseWellSchema, Well
from fiab.util.hruuid import hruuid
from fiab.util import scraper

from dataclasses import dataclass
from datetime import date, datetime
import time
import pytz

import pandas as pd

@dataclass
class YahooDailyTickerSchema(BaseWellSchema):
    ticker: str
    date: datetime
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int

@dataclass
class YahooOptionsTickerSchema(BaseWellSchema):
    ticker: str
    option: str # Either call or put
    strike: float
    contract: str
    last_trade: datetime
    price: float
    bid: float
    ask: float
    volume: int
    open_interest: int
    implied_volatility: float
    in_the_money: bool
    expires: datetime

class YahooDailyTickerWell(Well):
    index = 'yahoo.daily'
    frequency = '59 23 * * 1-5'  #: 23:59 every weekday
    well_data_schema: BaseWellSchema = YahooDailyTickerSchema

    def __init__(self, *args, ticker: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ticker

    def drill(self):
        if self.name is None:
            raise RuntimeError("No ticker specified")

        base = f'https://query1.finance.yahoo.com/v7/finance/download/{self.name}'

        query = '&'.join(f'{k}={v}' for k, v in {
            'period1': 0, # Start
            'period2': int(time.time()), # End
            'interval': '1d', # interval of data
            'events': 'history', # static
            'includeAdjustedClose': True # static
        }.items())

        target = f'{base}?{query}'
        
        # Get and parse data
        load_time = datetime.now()
        data: pd.DataFrame = pd.read_csv(target, parse_dates=['Date'])
        data.dropna(inplace=True)
        data['Volume'] = data['Volume'].astype(int)

        last_pull = self.meta.get(self.name, 0)
        self.meta = {self.name: int(data['Date'].max().strftime('%s'))}
        new_data = data[data['Date'] > datetime.fromtimestamp(last_pull)]

        # Convert to List[YahooDailyTickerSchema]
        rows = map(lambda t: t[1], new_data.iterrows())
        ticker_data = map(lambda row: YahooDailyTickerSchema(
            id=hruuid(),
            timestamp=load_time,
            ticker=self.name, 
            **{key.lower().replace(' ', '_'): value for key, value in dict(row).items()}
        ), rows)

        return list(ticker_data)


class YahooOptionsTickerWell(Well):
    index = 'yahoo.options.daily'
    frequency = '0,30 6-13 * * 1-5'  #: Every half hour during trading options trading hours
    well_data_schema = YahooOptionsTickerSchema

    def __init__(self, *args, ticker: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ticker

    def process_yahoo_table(self, date=''):
        "Converts the Yahoo HTML table into a pandas table"

        base_target = f'https://finance.yahoo.com/quote/{self.name}/options?straddle=false&date={date}'
        soup = scraper.get_soup(base_target)
        table_comps = {
            'option': [],
            'contract': [],
            'last_trade': [],
            'strike': [],
            'price': [],
            'bid': [],
            'ask': [],
            'change': [],
            'pct_change': [],
            'volume': [],
            'open_interest': [],
            'implied_volatility': [],
            'in_the_money': [],
        }
        row_names = (
            'contract', 'last_trade', 'strike',
            'price', 'bid', 'ask', 'change', 'pct_change', 'volume',
            'open_interest', 'implied_volatility'
        )
        strip_commas = lambda c: c.replace(',', '').strip()
        int_cast = lambda c: int(strip_commas(c)) if strip_commas(c[:-1]) else 0
        pct_cast = lambda c: float(strip_commas(c[:-1])) / 100 if strip_commas(c[:-1]) else 0.
        float_cast = lambda c: float(strip_commas(c)) if strip_commas(c[:-1]) else 0.
        row_casts = (
            str, lambda c: datetime.strptime(c, '%Y-%m-%d %I:%M%p EST').astimezone(pytz.timezone("US/Eastern")),
            float_cast, float_cast, float_cast, float_cast, float_cast, 
            pct_cast, int_cast, int_cast, pct_cast
        )

        for option in ['calls', 'puts']:
            option_table = soup.find('table', **{'class': option})
            for raw_row in option_table.find_all('tr', **{'class': 'BdT'}):
                in_the_money = 'in-the-money' in raw_row.attrs.get('class', [])
                row_values = [c.text for c in raw_row.children]
                parsed_row_values = map(
                    lambda p: p[0](p[1]), 
                    zip(row_casts, row_values)
                )

                row_dict = dict(zip(row_names, parsed_row_values))
                row_dict['option'] = option
                row_dict['in_the_money'] = in_the_money

                for key, value in row_dict.items():
                    table_comps[key].append(value)

        return pd.DataFrame(table_comps)

    def get_options_expiration_dates(self):
        base_target = f'https://finance.yahoo.com/quote/{self.name}/options?straddle=false'
        soup = scraper.get_soup(base_target)
        options = soup.find('select', **{'class': 'Bd'}).children
        return map(lambda o: int(o.attrs['value']), options)

    def drill(self, gid):
        ticker_data = []
        for date in self.get_options_expiration_dates():
            table = self.process_yahoo_table(date)
            table.drop(['change', 'pct_change'], axis=1, inplace=True)

            load_time = time.time()

            # Convert to List[YahooOptionsTickerSchema]
            rows = map(lambda t: t[1], table.iterrows())
            ticker_data.extend(map(lambda row: YahooOptionsTickerSchema(
                id=hruuid(),
                gid=gid,
                timestamp=load_time,
                ticker=self.name,
                expires=date,
                **{key.lower().replace(' ', '_'): value for key, value in dict(row).items()}
            ), rows))

        return ticker_data

#: Example Tickers:

if __name__ == "__main__":
    y = YahooDailyTickerWell(ticker='NOK')
    yo = YahooOptionsTickerWell(ticker='NOK')
    yo.reset()
    yo.run()
    z = YahooDailyTickerWell(ticker='QQQ').run()
    zo = YahooOptionsTickerWell(ticker='QQQ')
    zo.reset()
    zo.run()
    x = y.run()
    import pdb; pdb.set_trace()