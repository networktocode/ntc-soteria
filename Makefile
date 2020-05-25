.DEFAULT_GOAL := help

.PHONY: help
help:
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | \
	sort | \
	awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

pylint: ## Pylint
	pylint acl_auditor/ tests/

yamllint: ## Yamllint
	find ./ \( -name *.yaml -o -name *.yml \) | xargs

black: ## Black
	black acl_auditor/ tests/

pytest: ## Pytest
	pytest -vvv

#bandit:
#safety:
#mypy: 

# :%s/^[ ]\+/\t/g - automatically replace all tabs with spaces
