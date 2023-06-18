import io
import csv
import json
from operator import itemgetter
from collections import OrderedDict
from datetime import datetime, timedelta

import aiohttp
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

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
    async with session.post("http://pricing:8082", json=symbols) as response:
        response_data = await response.text()
        return json.loads(response_data)

async def generate_snapshot(limit):
    async with aiohttp.ClientSession() as session:
        # from cryptocompare API
        rankings_list = await get_rankings(session, limit)
        rankings_list = sorted(rankings_list, key=itemgetter('rank'))
        
        # # from coinmarketcap API
        symbols = [ranking['symbol'] for ranking in rankings_list]
        prices_dict = await get_prices(session, symbols)

        # Applys Price over Symbol Series, defaults to price from rankings if not availible
        for token in rankings_list:
            token['price'] = prices_dict[token['symbol']]
            if token.get('price') is None:
                token['price'] = token['CC_Price']
            del token['CC_Price']

        return rankings_list

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
    async with sessionmanager.session() as session:
        records = await get_tokens_by_date(rounded_dt, session)
        records = [record.__dict__ for record in records]

        # If no timestamp was given, but existing result is smaller than requests
        if do_it_live:
            if limit > len(records):
                # empty results to be overwritten
                records = []

    # no timestamp was given, and cache was unsatisfactory or non-existent
    if do_it_live and len(records) == 0:
        records = await generate_snapshot(limit)
        async with sessionmanager.session() as session:
            for row in records:
                row['created_at'] = rounded_dt
                token_row = TokenSchemaCreate(**row)
                await create_token(token_row, session)

    if len(records) != 0:
        # in case new limit is different than what was in the DB
        records = records[:limit]

        # get rid of unnessesary info and rename Price to match project spec
        # Rename and reorder columns
        column_renames = OrderedDict([
            ('rank', 'Rank'),
            ('symbol', 'Symbol'),
            ('price', 'Price USD')
        ])
        records = [{new: record[old] for old, new in column_renames.items()} for record in records]

        # output formatted to user request
        if format.lower() == 'json':
            return records
        else:
            with io.StringIO() as stream:
                writer = csv.DictWriter(stream, fieldnames=column_renames.values(), quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                writer.writerows(records)
                
                response = StreamingResponse(iter([stream.getvalue()]),
                                            media_type="text/csv"
                                            )
                response.headers["Content-Disposition"] = "attachment; filename=export.csv"
            return response
    else:
        return {
            'message': f'No results found at {rounded_dt} limit {limit}'
        }