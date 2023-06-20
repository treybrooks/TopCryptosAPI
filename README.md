# Top Cryptocurrency Price List

## Introduction
This project ties two external APIs together for a priced 24h volume ranked list of cryptocurrencies. A database stores requests for future reference and also acts like a cache to prevent redundant API calls.

## Guide to Setup and Run
1. *CRITICAL*: Be sure to do this before you run the project. Copy `.env.dev.example` to `.env.dev` in the same directory and replace the appropriate secrets for the project.
   * Without this you will not be able to connect to the database
2. Make sure the API keys are populated with the correct keys from the appropriate services.
   1. Ranking API: (CryptoCompare API)[https://www.cryptocompare.com/cryptopian/api-keys]
   2. Pricing API: (CoinMarketCap API)[https://pro.coinmarketcap.com/account]
3. Spin everything up: `make up`
4. Setup the database for your initial run: `make setup_db`
   * As the database is persistent, this will not be needed in subsequent runs
5. The Frontend API takes a few seconds to spin up as it waits for Postgres to be available.   
   * Once the API is running, try `curl http://0.0.0.0:6667?limit=10&format=json` from your console or use Postman if you like.
   * One can also explore the API and various endpoints at `0.0.0.0:6667/docs` as the project is created with FastAPI
6. Testing is provided in the makefile as well `make test`

## Endpoint Description
* Base URL: `0.0.0.0:6667`
* Parameters:
  * limit: Integer field defaulting to 100, but can be any positive whole number
  * dt: String field that defaults to `datetime.now()` and will be rounded down to 5 minutes for historical storage. example: `2023-06-15 17:35:00.000`
  * format: String field that defaults to `json` but any other text provided will return the data formatted as a `csv`

# About the project
### Technologies Used
* Python
  * asyncio, aiohttp
  * Pytest
* FastAPI
* Docker-compose
* Postgresql
  * Alembic for migrations
  * SQL Alchemy
* Git / Github

## Assumptions
* Only USD prices are needed (though could be changed in the `.env.dev` file)
* Single user/tenant
* Security measures like authorization not in scope
* User is responsible for setting historical snapshots
  * User understands that historical results are limited to number of cryptocurrencies requested at the time of the original request. i.e. If one requests 200 cryptos an hour ago, they will never be able to request more from that timestamp.
* User will keep a record of historical timestamps available, or be able to reference the database directly. 
  * An endpoint to list available historical statistics is in the future road-map.
* A 5 minute pseudo-cache is acceptable
* Two or more calls within the 5 minute cache window that require a higher limit than previously stored in that time window will overwrite previous prices

## Architecture design and implementation
In respect to building a service oriented architecture (SOA) project, Ranking (`:8081`) and Pricing (`:8082`) services can be called independently from the frontend API as they use FastAPI themselves. The database only communicates with the frontend to minimize coupling of services and ease of data modeling. The Frontend API (`:6667`) waits for all results from the ranking service before calling the pricing service to reduce unnecessary API credit use and ensure only the requested crypto tickers are returned. 

If not given a timestamp, the Frontend API checks if results exist within the current 5 minute window and that they are sufficient to fulfill the incoming request. Upon not finding sufficient data, the request is passed off to the external services to build a result. This result is then stored in Postgres and can be requested later.

Docker-compose was used as an orchestration tool to build and run all necessary services. All services use FastAPI to provide interservice communication. External requests are all made asynchronously to minimize wait times for server response. The Pricing service depends on the results of the Ranking service to ensure the optimal list of prices is returned (thus rendering services effectively sequential). 

Unit testing does not require the services to be running unless user is testing the database functionality, in which case only Postgres needs to run.

## Future Improvements
* Clean up requirements files for services as there are unneeded packages
* Separate testing packages from "production"
* Include parameter validation
* Add endpoint to provide available historical timestamps
* Include status messages for metadata and references for JSON requests
* Enable a form of authorization for the frontend API if the project is to be hosted externally
* Better error handling as response messages
* Connect Pricing API to database to store hash table for coin symbol to ID mapping, and provide an API endpoint to refresh this mapping

## Thoughts & Considerations
* We could integrate Pricing API into the Ranking service to start calling prices before all Rankings are returned, but this would require coupling the services.
* Message brokers or GRPC could be used instead of HTTP API intercommunication but was not given the size of the data, the pre-existing need for external APIs already, and to reduce the number of technologies used.

## Refferences
* https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
* https://ahmed-nafies.medium.com/fastapi-with-sqlalchemy-postgresql-and-alembic-and-of-course-docker-f2b7411ee396
* https://medium.com/freestoneinfotech/simplifying-docker-compose-operations-using-makefile-26d451456d63
