build:
	docker-compose -f docker-compose.yml build $(c)
up:
	docker-compose -f docker-compose.yml up $(c)
down:
	docker-compose -f docker-compose.yml down $(c)
logs:
	docker-compose -f docker-compose.yml logs --tail=100 -f $(c)
test:
	docker-compose -f docker-compose.yml exec ranking python -m pytest	
	docker-compose -f docker-compose.yml exec pricing python -m pytest
	docker-compose -f docker-compose.yml exec api python -m pytest
setup_db:
	docker-compose -f docker-compose.yml exec api alembic revision --autogenerate -m "Adding token model"
	docker-compose -f docker-compose.yml exec api alembic upgrade head