from fiab.base.well import BaseWellSchema, Well
from fiab.util.hruuid import hruuid

from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List

import time
import requests

TARGET = 'https://api.stocktwits.com/api/2/streams/trending.json'

@dataclass
class StockTwitMessage(BaseWellSchema):
    body: str
    create_date: datetime
    username: str
    join_date: datetime
    official: bool
    followers: int
    following: int
    ideas: int
    likes: int
    symbols: List[str]
    sentiment: Optional[str]

@dataclass
class StockTwitTrendingSymbol(BaseWellSchema):
    symbol: str

class StockTwitMessageWell(Well):
    name = 'StockTwit Trending Messages'
    index = 'stocktwit.message'
    frequency = '0,5,10,15,20,25,30,35,40,45,50,55 * * * *'
    last_run: Optional[datetime]
    well_data_schema = StockTwitMessage

    def drill(self, gid):
        response = requests.get(TARGET)
        if not response.ok:
            raise RuntimeError(response.json())

        load_time = time.time()
        messages = response.json()['messages']
        parsed = map(lambda msg: StockTwitMessage(
            id=hruuid(),
            gid=gid,
            timestamp=load_time,
            body=msg['body'],
            create_date=msg['created_at'],
            username=msg['user']['username'],
            join_date=msg['user']['join_date'],
            official=msg['user']['official'],
            followers=msg['user']['followers'],
            following=msg['user']['following'],
            ideas=msg['user']['ideas'],
            likes=msg.get('likes', {}).get('total'),
            symbols=list({s['symbol'] for s in msg['symbols']}),
            sentiment=(msg['entities'].get('sentiment') or {}).get('basic')
        ), messages)

        return list(parsed)

class StockTwitSymbolWell(Well):
    name = 'StockTwit Trending Symbols'
    index = 'stocktwit.symbol'
    frequency = '0,5,10,15,20,25,30,35,40,45,50,55 * * * *'
    last_run: Optional[datetime]
    well_data_schema = StockTwitTrendingSymbol

    def drill(self):
        response = requests.get(TARGET)
        if not response.ok:
            raise RuntimeError(response.json())

        symbols = set()
        load_time = time.time()
        messages = response.json()['messages']
        for msg in messages:
            symbols |= {s['symbol'] for s in msg['symbols']}

        parsed = map(lambda symbol: StockTwitTrendingSymbol(
            id=hruuid(),
            timestamp=load_time,
            symbol=symbol
        ), symbols)

        return list(parsed)

if __name__ == "__main__":
    x = StockTwitSymbolWell().run()
    import pdb; pdb.set_trace()