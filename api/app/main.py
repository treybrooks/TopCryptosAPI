from datetime import datetime, timedelta
import json
import aiohttp
import polars as pl

from fastapi import APIRouter, Depends
from .services.database import sessionmanager
from .models import TokenInfo
from .views.tokeninfo import create_token, TokenSchemaCreate, get_tokens_by_date


async def get_rankings(session, limit):
    parameters = {
    'limit': str(limit)
    }
    async with session.get("http://ranking:8081", params=parameters) as response:
        data = await response.text()
        return json.loads(data)
    
async def get_prices(session, symbols):
    parameters = {
    'symbols': ','.join(map(str, symbols))
    }
    async with session.get("http://pricing:8082", params=parameters) as response:
        data = await response.text()
        return json.loads(data)

async def generate_snapshot(limit):
    async with aiohttp.ClientSession() as session:
        # from cryptocompare API
        rankings_list = await get_rankings(session, limit)
        df = pl.DataFrame(rankings_list).sort('rank')
        
        # # from coinmarketcap API 
        symbols = df['symbol'].to_list()
        prices_dict = await get_prices(session, symbols)
        # Applys Price over Symbol Series, defaults to price from rankings if not availible
        df = df.with_columns(pl.col('symbol').map_dict(prices_dict, default=df['CC_Price']).alias('price'))

        return df

def round_minutes(dt: datetime, resolutionInMinutes: int = 5):
    # stolen from: https://gist.github.com/cupdike/c5554233e1dd6b233a9b6ec6adb05c5a
    """round_minutes(datetime, resolutionInMinutes) => datetime rounded to lower interval
    Works for minute resolution up to a day (e.g. cannot round to nearest week).
    """
    # First zero out seconds and micros
    dtTrunc = dt.replace(second=0, microsecond=0)
    # Figure out how many minutes we are past the last interval
    excessMinutes = (dtTrunc.hour*60 + dtTrunc.minute) % resolutionInMinutes
    # Subtract off the excess minutes to get the last interval
    return dtTrunc + timedelta(minutes=-excessMinutes)

router = APIRouter(tags=["main"])

@router.get("/")
async def root(limit: int = 100, dt: datetime = None, format: str = 'json'):
    if dt is None:
        do_it_live = True
        dt = datetime.now()
    else:
        do_it_live = False

    rounded_dt = round_minutes(dt)

    # query if data exists at timestamp
    # functions as psuedo cache
    results_df = None
    async with sessionmanager.session() as session:
        records = await get_tokens_by_date(rounded_dt, session)
        records = [record.__dict__ for record in records]
        results_df = pl.from_records(records)

    # no record exists in "cache" for given timestamp, if given at all
    if do_it_live and results_df.is_empty():
        results_df = await generate_snapshot(limit)
        async with sessionmanager.session() as session:
            for row in results_df.iter_rows(named=True):
                row['created_at'] = rounded_dt
                token_row = TokenSchemaCreate(**row)
                await create_token(token_row, session)

    if not results_df.is_empty():
        # get rid of unnessesary info and rename Price to match project spec
        results_df = results_df.select(pl.col("rank"), pl.col("symbol"), pl.col("price"))
        results_df = results_df.rename({
            "rank": "Rank",
            "symbol": "Symbol",
            "price": "Price USD"
            })

        # in case new limit is different than what was in the DB
        results_df = results_df.limit(limit)

        # output formatted to user request
        if format.lower() == 'json':
            return results_df.to_dicts()
        else:
            return results_df.write_csv(separator=",")
    else:
        return {
            'message': f'No results found at {rounded_dt} limit {limit}'
        }