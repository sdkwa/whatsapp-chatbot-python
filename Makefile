.PHONY: help clean install install-dev test lint format build upload-test upload check-dist

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install: ## Install package
	pip install -e .

install-dev: ## Install package with development dependencies
	pip install -e .[dev,webhook]

test: ## Run tests
	pytest

format: ## Format code
	python -m black .
	python -m isort .

format-check: ## Check code formatting
	python -m black --check .
	python -m isort --check-only .

lint: ## Run linting
	python -m flake8 sdkwa_whatsapp_chatbot tests examples
	python -m mypy sdkwa_whatsapp_chatbot

build: clean ## Build package
	python -m build

check-dist: ## Check distribution
	twine check dist/*

upload-test: build check-dist ## Upload to TestPyPI
	twine upload --repository testpypi dist/*

upload: build check-dist ## Upload to PyPI
	twine upload dist/*

version-patch: ## Bump patch version
	bump2version patch

version-minor: ## Bump minor version
	bump2version minor

version-major: ## Bump major version
	bump2version major
