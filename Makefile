.PHONY: install backend frontend migrate seed test build run docker-up docker-down
install:
	python -m pip install -r backend/requirements.txt
	cd frontend && npm install
backend:
	cd backend && python manage.py runserver
frontend:
	cd frontend && npm run dev
migrate:
	cd backend && python manage.py migrate
seed:
	cd backend && python manage.py seed_demo
test:
	cd backend && python manage.py test
	cd frontend && npm test
build:
	cd frontend && npm run build
docker-up:
	docker compose up --build -d
docker-down:
	docker compose down
