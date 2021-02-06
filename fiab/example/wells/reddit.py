from fiab.base.well import BaseWellSchema, Well
from fiab.util.hruuid import hruuid
from fiab.util import scraper

from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List
import time

TARGET = 'https://www.reddit.com/r/{subreddit}.json'

@dataclass
class RedditPostSchema(BaseWellSchema):
    subreddit: str
    author: str
    title: str
    flairs: List[str]
    ups: int
    downs: int
    awards: int
    created: datetime
    url: str
    comments: int

class RedditPostWell(Well):
    index = 'reddit.rising'
    frequency = '0,5,10,15,20,25,30,35,40,45,50,55 * * * *'
    well_data_schema: RedditPostSchema

    def drill(self):
        response = scraper.get(TARGET.format(subreddit=self.name))
        if not response.ok:
            raise RuntimeError(response.json())

        load_time = time.time()

        messages = map(lambda child: child['data'], response.json()['data']['children'])
        parsed = map(lambda msg: RedditPostSchema(
            id=hruuid(),
            timestamp=load_time,
            subreddit=self.name,
            author=msg['author'],
            title=msg['title'],
            flairs=[_['t'] for _ in msg['link_flair_richtext'] if 't' in _],
            ups=msg['ups'],
            downs=msg['downs'],
            awards=[*{_['name'] for _ in msg['all_awardings']}],
            created=msg['created_utc'],
            url=msg['url'],
            comments=msg['num_comments']
        ), messages)

        return list(parsed)

class WsbRedditPostWell(RedditPostWell):
    name = 'wallstreetbets'

class StocksRedditPostWell(RedditPostWell):
    name = 'stocks'

class PennyStocksRedditPostWell(RedditPostWell):
    name = 'pennystocks'

if __name__ == "__main__":
    x = WsbRedditPostWell().run()
    y = StocksRedditPostWell().run()
    z = PennyStocksRedditPostWell().run()
    