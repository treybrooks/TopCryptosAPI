import os
import json
import asyncio
import aiohttp
from  aiohttp import ClientConnectorError, ServerTimeoutError, TooManyRedirects
from aiolimiter import AsyncLimiter
from contextlib import asynccontextmanager
from fastapi import FastAPI, Path
import logging


# allow for 30 concurrent entries within a 60 second window
rate_limit = AsyncLimiter(30, 60)

default_currency = os.getenv('DEFAULT_CURRENCY','USD')

def chunk_list(to_chunk, size = 100):
    # utility function for pagination of lists
    # looping till length size
    for i in range(0, len(to_chunk), size):
        yield to_chunk[i:i + size]

def parse_pricing(data):
    pricing = {}
    for value in data.values():
        pricing[value['symbol']] = value.get('quote', {}).get(default_currency, {}).get('price')
    return pricing

async def get_pricing_page(ids: list = None):
    url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    parameters = {
        'convert': default_currency,
        'id': ','.join(map(str, ids))
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.getenv('COINMARKETCAP_KEY'),
    }    

    async with aiohttp.ClientSession() as session:
        session.headers.update(headers)
        async with session.get(url, params=parameters) as response:
            if response.status == 200:
                result = json.loads(await response.text())
                return parse_pricing(result['data'])
            else:
                print(response.status, await response.text())
                return {}

async def get_coinmarketcap_map():
    logging.info('Setting coin_map')
    
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': os.getenv('COINMARKETCAP_KEY'),
    }

    async with aiohttp.ClientSession() as session:
        session.headers.update(headers)
        async with session.get(url) as response:
            data_json = json.loads(await response.text())
            return {coin['symbol']: coin['id'] for coin in data_json['data']}

COIN_MAP = {}
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load Coin to ID map from coinmarketcap API before we start taking requests
    global COIN_MAP
    COIN_MAP = await get_coinmarketcap_map()
    logging.info(f'Lifespan COIN_MAP: {len(COIN_MAP)} of type {type(COIN_MAP)}')
    yield
    COIN_MAP.clear()

app = FastAPI(lifespan=lifespan)

@app.post("/")
async def get_pricing(symbols: list[str] = [], sng_page_limit: int = 500):
    coin_ids = [COIN_MAP.get(symbol) for symbol in symbols if COIN_MAP.get(symbol)]

    if len(symbols) <= sng_page_limit:
        # if pagination is not needed
        async_results = await get_pricing_page(coin_ids)
    else:
        # request pages async
        rank_tasks = []
        for ids_chunk in chunk_list(coin_ids, sng_page_limit):
            rank_tasks.append(
                asyncio.create_task(get_pricing_page(ids_chunk))
            )
        
        list_results = await asyncio.gather(*rank_tasks)
        # Create Mapping dict of symbol to price
        async_results = {k: v for d in list_results for k, v in d.items()}

    return async_results