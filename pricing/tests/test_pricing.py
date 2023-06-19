import json
from pathlib import Path
from collections.abc import Sequence
from unittest.mock import patch

import pytest

from app.main import app, parse_pricing, get_pricing, get_pricing_page, chunk_list, get_coinmarketcap_map


with Path('tests/mock_data/pricing_response.json').open('r', encoding='UTF-8') as f:
    mocked_data = json.load(f)

with Path('tests/mock_data/coinmap_response.json').open('r', encoding='UTF-8') as f:
    mocked_coinmap = json.load(f)

class MockResponse:
    def __init__(self, text, status):
        self._text = text
        self.status = status

    async def text(self):
        return self._text

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self

def test_parse_pricing():
    data = mocked_data['data']
    parsed = parse_pricing(data)
    assert type(parsed) == type({})
    
    for symbol, price in parsed.items():
        assert type(symbol) is str
        assert type(price) is float or None

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_get_pricing_page(mocker):
    resp = MockResponse(json.dumps(mocked_data), 200)
    mocker.return_value.__aenter__.return_value = resp

    ids = [1,1027]
    price_dict = await get_pricing_page(ids)
    assert type(price_dict) is dict

    for symbol, price in price_dict.items():
        assert type(symbol) is str
        assert type(price) is float or None
    
def test_chunk_list():
    to_chunk = [1,2,3,4,5,6,7,8,9,10,11,12] 
    size = 5
    result = chunk_list(to_chunk, size)
    for res in result:
        assert len(res) <= size

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_get_pricing(mocker):
    resp = MockResponse(json.dumps(mocked_data), 200)
    mocker.return_value.__aenter__.return_value = resp

    symbols = ['BTC','ETH']
    results = await get_pricing(symbols)
    assert type(results) is dict

    for symbol, price in results.items():
        assert type(symbol) is str
        assert type(price) is float

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_get_coinmarketcap_map(mocker):
    resp = MockResponse(json.dumps(mocked_coinmap), 200)
    mocker.return_value.__aenter__.return_value = resp

    parsed_mocked_data = {coin['symbol']: coin['id'] for coin in mocked_coinmap['data']}
    symbols, ids  = list(zip(*parsed_mocked_data.items()))

    coin_map = await get_coinmarketcap_map()
    assert set(symbols) == set(coin_map.keys())
    assert set(ids) == set(coin_map.values())
