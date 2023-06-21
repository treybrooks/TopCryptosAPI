import os
import math
import json
import asyncio
from operator import itemgetter

import aiohttp
from  aiohttp import ClientConnectorError, ServerTimeoutError, TooManyRedirects
from aiolimiter import AsyncLimiter
from fastapi import FastAPI, Path

app = FastAPI()
# allow for 10 concurrent entries within a 2 second window
rate_limit = AsyncLimiter(10, 2)

default_currency = os.getenv('DEFAULT_CURRENCY','USD')

def parse_data(datum):
    return {
        "symbol": datum.get("CoinInfo", {}).get("Name"),
        "CC_Price": datum.get("RAW", {}).get("USD", {}).get("PRICE")
    }

async def get_numbered_ranking_page(limit:int = 100, page:int = 0):
    async with rate_limit:
        response = await call_cryptocompare(limit, page)
        if response['Data']:
            parsed_data = [parse_data(datum) for datum in response['Data']]
            return (page, parsed_data)
        else:
            print(f"nothing found at page {page}: {response}")
            return (page, [])

async def call_cryptocompare(limit:int = 100, page:int = 0):
    url = 'https://min-api.cryptocompare.com/data/top/totalvolfull'
    parameters = {
    'limit': str(limit),
    'page': str(page),
    'tsym': default_currency
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.getenv('CRYPTOCOMPARE_KEY'),
    }

    async with aiohttp.ClientSession() as session:
        session.headers.update(headers)
        async with session.get(url, params=parameters) as response:
            if response.status == 200:
                return json.loads(await response.text())
            else:
                print(response.status, await response.text())
                return {}

@app.get("/")
async def get_rankings(limit: int = 1000, single_page_limit: int = 100):
    if limit <= single_page_limit:
        # if pagination is not needed
        async_results = await get_numbered_ranking_page(limit)
        async_results = [async_results]
    else:
        # request pages async
        rank_tasks = []
        semaphore = asyncio.Semaphore(20)
        for page in range(math.ceil(limit/single_page_limit)):
            rank_tasks.append(
                asyncio.create_task(get_numbered_ranking_page(single_page_limit, page))
            )
        async_results = await asyncio.gather(*rank_tasks)
        
    # rank and sort results based on page and order
    rank_data = []
    for page_results in async_results:
        page, page_rankings = page_results
        for rank, coin in enumerate(page_rankings):
            coin['rank'] = page*single_page_limit + (rank+1)
            rank_data.append(coin)
    return sorted(rank_data, key=itemgetter('rank'))
