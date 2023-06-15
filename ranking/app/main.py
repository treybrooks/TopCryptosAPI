import os
import math
import json
from datetime import datetime
import asyncio

import aiohttp
from  aiohttp import ClientConnectorError, ServerTimeoutError, TooManyRedirects
from fastapi import FastAPI

app = FastAPI()

default_currency = 'USD'

def parse_data(datum):
    return {
        "symbol": datum.get("CoinInfo", {}).get("Name"),
        "CC_Price": datum.get("RAW", {}).get("USD", {}).get("PRICE")
    }

async def get_ranking_page(limit = 100, page = 0):
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

    try:
        async with aiohttp.ClientSession() as session:
            session.headers.update(headers)
            async with session.get(url, params=parameters) as response:
                data = await response.text()
                result = json.loads(data)
                if result['Data']:
                    parsed_data = [parse_data(datum) for datum in result['Data']]
                    return (page, parsed_data)

    except (ClientConnectorError, ServerTimeoutError, TooManyRedirects) as e:
        print(e)

async def get_rankings(limit_total=1000, sng_page_limit=100):
    if limit_total <= sng_page_limit:
        # if pagination is not needed
        async_results = await get_ranking_page(limit_total)
        async_results = dict([async_results])
    else:
        # request pages async
        rank_tasks = []
        for page in range(math.ceil(limit_total/sng_page_limit)):
            rank_tasks.append(
                asyncio.create_task(get_ranking_page(sng_page_limit, page))
            )
        
        async_results = dict(await asyncio.gather(*rank_tasks))

    # take async results, and put them back in order
    results = []
    for i in range(len(async_results)):
        results += async_results[i]

    # Format data here to minimize size for network transfer
    rank_data = []
    for rank, coin in enumerate(results):
        coin['rank'] = rank+1
        rank_data.append(coin)

    return rank_data

@app.get("/")
async def root(limit: int = 200, dt: datetime = None):
    return await get_rankings(limit_total = limit)
