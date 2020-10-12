up:
	docker-compose up backend
freeze:
	pip freeze | grep -v "pkg-resources" > requirements.txt

migrations:
	@docker exec -it backend alembic revision --autogenerate;

migrate:
	@docker exec -it backend alembic upgrade head;
