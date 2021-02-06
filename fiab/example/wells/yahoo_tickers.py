from fiab.base.well import BaseWellSchema, Well
from fiab.util.hruuid import hruuid

from dataclasses import dataclass
from datetime import date, datetime
import time

import pandas as pd

@dataclass
class YahooDailyTickerSchema(BaseWellSchema):
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int

class YahooTickerWell(Well):
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


#: Example Tickers:

if __name__ == "__main__":
    y = YahooTickerWell(ticker='NOK')
    z = YahooTickerWell(ticker='QQQ').run()
    x = y.run()
    import pdb; pdb.set_trace()