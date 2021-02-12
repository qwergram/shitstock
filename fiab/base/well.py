from typing import Optional, List, Generic, TypeVar, Any, Dict
from datetime import datetime, date
import io
import pickle
import json

from dataclasses import dataclass
import requests

from fiab.util.logger import DEFAULT_LOGGER
from fiab.util.hruuid import hruuid
from fiab.settings import ELASTIC_SEARCH_URL

@dataclass
class BaseWellSchema:
    id: str
    timestamp: Optional[datetime]
    gid: Optional[str]

    def json(self):
        data_contents = {}
        for key in self.__dataclass_fields__.keys():
            value = getattr(self, key)
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S.%f')
            if key == 'timestamp':
                key = f'@{key}'

            data_contents[key] = value
        
        # Try to json dump the contents
        json.dumps(data_contents)

        return data_contents
        

@dataclass
class Well:
    name: str  #: 
    index: str  #: elastic search index where this will appear
    frequency: Optional[str]  #: Cron format, leave None for one time run only
    well_data_schema: BaseWellSchema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def reset(self):
        DEFAULT_LOGGER.debug(f'Resetting {self.index}')
        self.meta = None

        index_target = f'{ELASTIC_SEARCH_URL}/{self.index}'

        index_exists = requests.get(index_target).ok

        if index_exists:
            delete_response = requests.delete(index_target)
            if not delete_response.ok:
                raise RuntimeError(delete_response.json())
        
        put_response = requests.put(index_target)
        if not put_response.ok:
            raise RuntimeError(put_response.json())

    @property
    def meta(self):
        DEFAULT_LOGGER.debug(f'Loading {self.index} meta')

        meta_exists = requests.get(f'{ELASTIC_SEARCH_URL}/meta').ok
        if not meta_exists:
            put_response = requests.put(f'{ELASTIC_SEARCH_URL}/meta')
            if not put_response.ok:
                raise RuntimeError(put_response.json())

        response = requests.get(f'{ELASTIC_SEARCH_URL}/meta/_doc/{self.index}')
        response_json = response.json()

        if not response.ok and response_json['found']:
            raise RuntimeError(response_json)

        if response_json['found']:
            return response_json['_source']
        return {}

    @meta.setter
    def meta(self, value: Optional[Dict[str, Any]]):
        DEFAULT_LOGGER.debug(f'Setting {self.index} meta')
        meta_target = f'{ELASTIC_SEARCH_URL}/meta/_doc/{self.index}'
        meta_index_exists = requests.get(f'{ELASTIC_SEARCH_URL}/meta').ok
        meta_data_exists = requests.get(meta_target).ok
        
        if not meta_index_exists:
            response = requests.put(f'{ELASTIC_SEARCH_URL}/meta')
            if not response.ok:
                raise RuntimeError(response.json())

        if value is None:
            if meta_data_exists:
                response = requests.delete(meta_target)
                if not response.ok:
                    raise RuntimeError(response.json())

        else:
            value = self.meta | value
            if meta_data_exists:
                requests.post(
                    meta_target.replace('_doc', '_update'),
                    json={
                        'doc': value
                    }
                )
            else:
                requests.post(
                    meta_target.replace('_doc', '_create'),
                    json=value
                )

    def drill(self, gid) -> List[BaseWellSchema]:
        raise NotImplementedError()

    def cache(self, data: List[BaseWellSchema]):
        filename = f'{self.index}-{self.name}.pkl'
        DEFAULT_LOGGER.info(f"Caching {len(data)} schemas to {filename}")
        
        with io.open(filename, 'wb') as handle:
            pickle.dump(data, handle)

    def load(self) -> List[BaseWellSchema]:
        filename = f'{self.index}-{self.name}.pkl'
        DEFAULT_LOGGER.info(f"Loading schemas from {filename}")

        with io.open(filename, 'rb') as handle:
            data = pickle.load(handle)

        return data

    def upload(self, schema: BaseWellSchema) -> str:
        DEFAULT_LOGGER.debug(f"Uploading {schema.id} to {self.index}")
        blob = schema.json()
            
        response = requests.post(
            f'{ELASTIC_SEARCH_URL}/{self.index}/_create/{schema.id}',
            json=blob,
        )

        if not response.ok:
            raise RuntimeError(response.json())

        payload = response.json()
        doc_index = payload['_index']
        doc_id = payload['_id']
        doc_type = payload['_type']

        return f'{ELASTIC_SEARCH_URL}/{doc_index}/{doc_type}/{doc_id}'

    def run(self) -> List[str]:
        DEFAULT_LOGGER.info(f"Running {self.index} ({self.name})")
        urls = []
        gid = hruuid()
        schemas = self.drill(gid)
        self.cache(schemas)
        DEFAULT_LOGGER.info(f"Using index: {self.index}")
        response = requests.put(f'{ELASTIC_SEARCH_URL}/{self.index}')
        if not response.ok and 'already exists' not in response.json()['error']['root_cause'][0]['reason']:
            raise RuntimeError(response.json())
        
        for schema in schemas:
            url = self.upload(schema)
            urls.append(url)
    
        DEFAULT_LOGGER.info(f'Uploaded {len(urls)} data points as {gid}')

        self.meta = {'gid': gid}

        return urls

    @property
    def data(self) -> List[BaseWellSchema]:
        gid = self.meta.get('gid')
        if gid is None:
            return []
        
        DEFAULT_LOGGER.debug(f'Loading {gid} run data')

        index_exists = requests.get(f'{ELASTIC_SEARCH_URL}/{self.index}').ok
        if not index_exists:
            return []

        response = requests.post(
            f'{ELASTIC_SEARCH_URL}/{self.index}/_search/',
            json={'query': {'match': {'gid': gid}}}
        )
        response_json = response.json()

        if not response.ok:
            raise RuntimeError(response_json)

        hits = response_json['hits']['hits']
        sources = list(map(lambda _: _['_source'], hits))
        timestamps = list(map(lambda _: _.pop('@timestamp'), sources))
        fixed = list(map(lambda p: p[0].__setitem__('timestamp', p[1]), zip(sources, timestamps)))
        results = list(map(lambda _: self.well_data_schema(**_), sources))

        return results