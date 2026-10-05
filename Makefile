.PHONY: help install seed run-api run-ui simulate test docker-up docker-down clean

help:
	@echo "StrataSentry-NWIS Operational Targets:"
	@echo "  make install     - Install Python & Node dependencies"
	@echo "  make seed        - Populate local database with synthetic Assam Basin data"
	@echo "  make run-api     - Start FastAPI backend with hot-reload"
	@echo "  make run-ui      - Start Next.js Drilling Dashboard"
	@echo "  make simulate    - Run real-time telemetry streaming simulator with packoff anomaly"
	@echo "  make test        - Run all pytest test suites"
	@echo "  make docker-up   - Launch full microservices stack via Docker Compose"
	@echo "  make docker-down - Stop Docker Compose services"
	@echo "  make clean       - Remove cache and temporary artifacts"

install:
	python -m pip install --upgrade pip
	pip install -r apps/api/requirements.txt
	cd apps/dashboard && npm install

seed:
	python scripts/seed_database.py

run-api:
	uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000 --reload

run-ui:
	cd apps/dashboard && npm run dev

simulate:
	python scripts/simulate_telemetry.py --well NHK-421 --rate-hz 2 --inject-incident packoff

test:
	pytest services/ tests/ apps/api/tests/ -v

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
