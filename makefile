build:
	docker-compose -f docker-compose.yml build $(c)
up:
	docker-compose -f docker-compose.yml up -d $(c)
dev:
	docker-compose -f docker-compose.yml up $(c)
start:
	docker-compose -f docker-compose.yml start $(c)
down:
	docker-compose -f docker-compose.yml down $(c)
destroy:
	docker-compose -f docker-compose.yml down -v $(c)
stop:
	docker-compose -f docker-compose.yml stop $(c)
restart:
	docker-compose -f docker-compose.yml stop $(c)
	docker-compose -f docker-compose.yml up -d $(c)
logs:
	docker-compose -f docker-compose.yml logs --tail=100 -f $(c)
test:
	docker-compose -f docker-compose.yml exec ranking python -m pytest	
	docker-compose -f docker-compose.yml exec pricing python -m pytest
setup_db:
	docker-compose -f docker-compose.yml exec api alembic revision --autogenerate -m "Adding token model"
	docker-compose -f docker-compose.yml exec api alembic upgrade head