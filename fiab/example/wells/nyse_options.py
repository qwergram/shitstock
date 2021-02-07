from fiab.base.well import Well, BaseWellSchema
from fiab.util import scraper
from fiab.util.hruuid import hruuid
from dataclasses import dataclass

import pandas as pd
import time

@dataclass
class NyseWeeklyOptionsSchema(BaseWellSchema):
    ticker: str

class NyseOptionsWeekliesWell(Well):
    name = 'NYSE Weekly Options List'
    index = 'nyse.options.weekly'
    frequency = '0 0 * * *'
    well_data_schema: NyseWeeklyOptionsSchema

    def pull_table(self):
        target = 'https://www.nyse.com/products/options-nyse-american-short-term'

        soup = scraper.get_soup(target)
        raw_table = soup.find('tbody').find_all('tr')
        tds = map(lambda tr: tr.find_all('td'), raw_table)
        processed_table = map(lambda tr: [_.text for _ in tr], tds)
        split_by_column = zip(*processed_table)
        
        return pd.DataFrame(data={
            'ticker': next(split_by_column), 
            'company': next(split_by_column)
        })

    def drill(self):
        table = self.pull_table()
        pull_time = time.time()
        schemas = map(lambda t: NyseWeeklyOptionsSchema(
            id=hruuid(),
            timestamp=pull_time,
            ticker=t
        ), table['ticker'])

        return list(schemas)

if __name__ == "__main__":
    x = NyseOptionsWeekliesWell().run()

