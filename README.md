# Fortris Takehome Code Evaluation

# Setup and Run
1. Use the `.env.dev.example` to build an appropriate `.env.dev` file to connect to the DB
2. Make sure those API keys are populated with the correct keys from the appropirate services
3. `docker-compose up --build`
    1. `docker exec api alembic revision --autogenerate -m "Adding token model"`
    2. `docker exec api alembic upgrade head`
4. feel free to `curl http://0.0.0.0:6667?limit=10&format=json` or use Postman if you like

* You can also explore the API at `0.0.0.0:6667/docs` as we're using FastAPI


## Inspirations
* https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html
* https://ahmed-nafies.medium.com/fastapi-with-sqlalchemy-postgresql-and-alembic-and-of-course-docker-f2b7411ee396
