project_dit = .
.PHONY: dev
dev:
	docker compose up postgres -d --remove-orphans

.PHONY: run-dev
run-dev: dev
	uvicorn main:app --reload 



.PHONY: dev-down
dev-down:
	docker compose down --remove-orphans --volumes

.PHONY: migration
migration:
	alembic revision \
	  --autogenerate \
	  --rev-id $(shell python migrations/_get_next_revision_id.py) \
	  --message $(message)

.PHONY: migrate
migrate:
	alembic upgrade head

.PHONY: run
run: migrate
	uvicorn main:app --host 0.0.0.0 --port 8000