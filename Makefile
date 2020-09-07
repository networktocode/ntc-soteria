.DEFAULT_GOAL := help

DOCKER_IMAGE = networktocode/ntc-soteria
DOCKER_VER = 0.0.1

.PHONY: help
help:
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | \
	sort | \
	awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker container.
	docker build -t $(DOCKER_IMAGE):$(DOCKER_VER) .

flake8: ## Python linting via Flake8.
	find . -name '*.py' -exec flake8 {} +

yamllint: ## YAML linting via Yamllint.
	find \( -name *.yaml -o -name *.yml \) | xargs yamllint -d "{ignore: docker-compose.yml}"

black: ## Format checking via Black.
	black --check . 

pytest: ## Unit tests via Pytest.
	pytest -vvv	

bandit: ## Security checks via Bandit.
	bandit --recursive --config .bandit.yml .

tests: flake8 yamllint black pytest bandit ## Format, lint, security and unit tests

# :%s/^[ ]\+/\t/g - automatically replace all tabs with spaces
