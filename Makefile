.DEFAULT_GOAL := help

.PHONY: help
help:
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | \
	sort | \
	awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

pylint: ## Python linting via Pylint.
	find . -name venv -prune -o -name '*.py' -exec pylint {} +

yamllint: ## YAML linting via Yamllint.
	find . \( -name *.yaml -o -name *.yml \) | xargs yamllint

black: ## Format checking via Black.
	black --check . --exclude venv/

pytest: ## Unit tests via Pytest.
	pytest -vvv	

bandit: ## Security checks via Bandit.
	bandit --exclude ./venv --recursive --config .bandit.yml .

tests: pylint yamllint black pytest bandit pytest ## Format, lint, security and unit tests

# :%s/^[ ]\+/\t/g - automatically replace all tabs with spaces
