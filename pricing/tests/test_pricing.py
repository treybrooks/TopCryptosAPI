import json
from pathlib import Path
from collections.abc import Sequence

from pydantic import BaseModel
from fastapi.testclient import TestClient

import asyncio
import pytest
import pytest_asyncio.plugin

from app.main import app, parse_pricing, get_pricing, get_pricing_page, chunk_list, get_coinmarketcap_map


client = TestClient(app)

with Path('tests/data/pricing_data.json').open('r', encoding='UTF-8') as f:
    response = json.load(f)

def test_parse_pricing():
    data = response['data']
    parsed = parse_pricing(data)
    assert type(parsed) == type({})
    
    for symbol, price in parsed.items():
        assert type(symbol) is str
        assert type(price) is float or None

@pytest.mark.asyncio
async def test_get_pricing_page():
    ids = [1,1027]
    price_dict = await get_pricing_page(ids)
    assert type(price_dict) is dict

    for symbol, price in price_dict.items():
        assert type(symbol) is str
        assert type(price) is float or None
    
def test_chunk_list():
    l = [1,2,3,4,5,6,7,8,9,10,11,12] 
    size = 5
    result = chunk_list(l, size)
    for res in result:
        assert len(res) <= size

@pytest.mark.asyncio
async def test_get_pricing():
    symbols = ['BTC','ETH','LTC','XRP','UDST']
    results = await get_pricing(symbols)
    assert type(results) is dict

    for symbol, price in results.items():
        assert type(symbol) is str
        assert type(price) is float

@pytest.mark.asyncio
async def test_get_coinmarketcap_map():
    coin_map = await get_coinmarketcap_map()
    for key, value in coin_map.items():
        assert type(key) is str
        assert type(value) is int

def test_root():
    symbols = ['BTC','ETH','LTC','XRP','UDST']
    results = client.post("/", json={'symbols': symbols})
    assert type(results) is dict

    for symbol, price in results.items():
        assert type(symbol) is str
        assert type(price) is float