from datetime import datetime, timedelta
import json
from pathlib import Path
from collections.abc import Sequence
from unittest.mock import patch, Mock, DEFAULT, AsyncMock
import aiohttp
import pytest
import contextlib


from app.main import get_rankings, get_prices, generate_snapshot, round_minutes, root


with Path('tests/mock_data/ranking_response.json').open('r', encoding='UTF-8') as f:
    mocked_ranking = json.load(f)
with Path('tests/mock_data/pricing_response.json').open('r', encoding='UTF-8') as f:
    mocked_pricing = json.load(f)

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
    
@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_get_rankings(mocker):
    resp = MockResponse(json.dumps(mocked_ranking), 200)
    mocker.return_value.__aenter__.return_value = resp
    
    async with aiohttp.ClientSession() as session:
        rankings = await get_rankings(session, 10)
    assert rankings == mocked_ranking

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post')
async def test_get_prices(mocker):
    resp = MockResponse(json.dumps(mocked_pricing), 200)
    mocker.return_value.__aenter__.return_value = resp

    async with aiohttp.ClientSession() as session:
        pricing = await get_prices(session, [])
    assert pricing == mocked_pricing

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
@patch('aiohttp.ClientSession.post')
async def test_generate_snapshot(mock_post, mock_get):
    resp = MockResponse(json.dumps(mocked_ranking), 200)
    mock_get.return_value.__aenter__.return_value = resp

    resp = MockResponse(json.dumps(mocked_pricing), 200)
    mock_post.return_value.__aenter__.return_value = resp

    with Path('tests/mock_data/snapshot_result.json').open('r', encoding='UTF-8') as f:
        snapshot_result = json.load(f)
    snapshot = await generate_snapshot(limit=10)
    assert snapshot == snapshot_result

def test_round_minutes():
    base = datetime.strptime("2023-06-19 00:00:00", "%Y-%m-%d %H:%M:%S")
    minutes_in_day = 24*60
    timestamp_list = [base + timedelta(minutes=x) for x in range(minutes_in_day)]
    
    timestamp_list = [round_minutes(timestamp) for timestamp in timestamp_list]
    assert len(set(timestamp_list)) == 24*12


# @pytest.mark.asyncio
# @patch('aiohttp.ClientSession.get')
# @patch('aiohttp.ClientSession.post')
# async def test_root(mock_post, mock_get):
#     resp = MockResponse(json.dumps(mocked_ranking), 200)
#     mock_get.return_value.__aenter__.return_value = resp

#     resp = MockResponse(json.dumps(mocked_pricing), 200)
#     mock_post.return_value.__aenter__.return_value = resp

#     with Path('tests/mock_data/root_response.json').open('r', encoding='UTF-8') as f:
#         root_result = json.load(f)
#     response = await root(limit=10)
#     assert response == root_result
