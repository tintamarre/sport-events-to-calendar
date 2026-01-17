.PHONY: help install dev build preview clean docker-dev docker-prod docker-stop docker-clean

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make dev            - Start development server"
	@echo "  make build          - Build for production"
	@echo "  make preview        - Preview production build"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make docker-dev     - Start development server in Docker"
	@echo "  make docker-prod    - Build and run production server in Docker"
	@echo "  make docker-stop    - Stop Docker containers"
	@echo "  make docker-clean   - Clean Docker containers and images"

install:
	npm ci

dev:
	npm run dev

build:
	npm run build

preview:
	npm run preview

clean:
	rm -rf ../docs node_modules

docker-dev:
	docker-compose up dev

docker-prod:
	docker-compose up --build prod

docker-stop:
	docker-compose down

docker-clean:
	docker-compose down -v --rmi all
