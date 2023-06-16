import json
from pathlib import Path
from collections.abc import Sequence

from pydantic import BaseModel
from fastapi.testclient import TestClient

import asyncio
import pytest
import pytest_asyncio.plugin

from app.main import app, parse_data, get_ranking_page, get_rankings


client = TestClient(app)

with Path('tests/data/ranking_data.json').open('r', encoding='UTF-8') as f:
    response = json.load(f)

def test_parse_data():
    for datum in response['Data']:
        parsed = parse_data(datum)
        assert len(parsed) == 2
        assert 'symbol' in parsed
        assert type(parsed['symbol']) == type('symbol')

@pytest.mark.asyncio
async def test_get_ranking_page_valid():
    single_page_limit = 10
    page = 0

    result = await get_ranking_page(single_page_limit, page)
    assert isinstance(result, Sequence)

@pytest.mark.asyncio
async def test_get_ranking_page_invalid():
    single_page_limit = 100
    page = 10000
    
    result = await get_ranking_page(single_page_limit, page)
    assert isinstance(result, Sequence)
    assert len(result) == 2
    assert len(result[1]) == 0

@pytest.mark.asyncio
async def test_get_rankings():
    limit_total=20

    result = await get_rankings(limit_total)
    assert isinstance(result, Sequence)
    assert len(result) == limit_total
    for res in result:
        assert type(res['rank']) == type(1)
        assert type(res['symbol']) == type('BTC')

def test_root():
    """
    Make sure a list of dicts is returned with the correct structure"""
    limit = 5
    response = client.get("/")
    data = response.json()

    assert len(data) == limit

    for datum in data:
        assert 'rank' in datum
        assert 'symbol' in datum

    assert data[0]['symbol'] == 'BTC'
