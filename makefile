build:
	docker-compose -f docker-compose.yml build $(c)
up:
	docker-compose -f docker-compose.yml up $(c) --scale test_postgres=0
down:
	docker-compose -f docker-compose.yml down $(c)
logs:
	docker-compose -f docker-compose.yml logs --tail=100 -f $(c)
test:
	docker-compose -f docker-compose.yml up -d
	docker-compose -f docker-compose.yml exec ranking python -m pytest	
	docker-compose -f docker-compose.yml exec pricing python -m pytest
	docker-compose -f docker-compose.yml exec api python -m pytest
	docker-compose -f docker-compose.yml down test_postgres
setup_db:
	docker-compose -f docker-compose.yml exec api alembic revision --autogenerate -m "Adding token model"
	docker-compose -f docker-compose.yml exec api alembic upgrade head