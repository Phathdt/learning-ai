.PHONY: help build run clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the binary
	go build -o lession2 main.go

run: ## Run the application
	go run main.go


clean: ## Remove built binary
	rm -f lession2

test: ## Run tests
	go test -v ./...

deps: ## Download dependencies
	go mod download
	go mod tidy

.env: ## Create .env from .env.example
	cp .env.example .env
	@echo "Don't forget to update .env with your API key!"
