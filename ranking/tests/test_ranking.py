import json
from pathlib import Path
from collections.abc import Sequence
from unittest.mock import patch

import pytest

from app.main import call_cryptocompare, parse_data, get_numbered_ranking_page, get_rankings


with Path('tests/mock_data/ranking_response.json').open('r', encoding='UTF-8') as f:
    mocked_data = json.load(f)

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
    
def test_parse_data():
    for datum in mocked_data['Data']:
        parsed = parse_data(datum)
        assert len(parsed) == 2
        assert 'symbol' in parsed
        assert type(parsed['symbol']) == type('symbol')

    
@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_call_cryptocompare(mocker):
    resp = MockResponse(json.dumps(mocked_data), 200)
    mocker.return_value.__aenter__.return_value = resp

    response = await call_cryptocompare()
    assert response == mocked_data

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_get_numbered_ranking_page(mocker):
    resp = MockResponse(json.dumps(mocked_data), 200)
    mocker.return_value.__aenter__.return_value = resp

    response = await get_numbered_ranking_page(limit=10)
    assert len(response[1]) == len(mocked_data['Data'])
    assert isinstance(response, Sequence)
    assert len(response) == 2

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_get_rankings(mocker):
    resp = MockResponse(json.dumps(mocked_data), 200)
    mocker.return_value.__aenter__.return_value = resp

    response = await get_rankings(limit=10)
    assert isinstance(response, Sequence)
    assert len(response) == 10
    for res in response:
        assert type(res['rank']) == type(1)
        assert type(res['symbol']) == type('BTC')
