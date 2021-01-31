import requests
from enum import Enum
from bs4 import BeautifulSoup

class UserAgent(Enum):
    truth = 'FIAB/1.0 (Python 3)'
    win_10_msft_edge = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53'

def get(url: str, *, user_agent: UserAgent = UserAgent.truth, **kwargs) -> requests.Response:
    return requests.get(
        url=url,
        headers={
            'User-agent': str(user_agent),
            **(kwargs.get('headers', {}))
        }
    )

def get_soup(*args, **kwargs) -> BeautifulSoup:
    return BeautifulSoup(get(*args, **kwargs).text, 'html.parser')