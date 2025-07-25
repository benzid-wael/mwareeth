# If the first argument is "run"...
ifeq (startapp,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "run"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # APP_NAME := $(strip $(word 1, $(RUN_ARGS)))
  APP_NAME := $(word 1, $(RUN_ARGS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif


clean-pyc:
	@find . -name __pycache__ -exec rm -rf {} \;

clean-coverage:
	@rm -rf .coverage htmlcov

clean: clean-pyc clean-coverage
	@rm -rf .cache .pyre .pytest_cache

flake8:
	uv run flake8 .

black:
	uv run black . --fast --line-length 120

pyre:
	uv run pyre check

polint:
	uv run polint

lint: flake8 pyre polint
	uv run dotenv-linter lint config/.env.template

pysa:
	uv run pyre analyze

safety:
	uv run safety check

freeze:
	uv run pip freeze

security: pysa safety

extract-messages:
	uv run setup.py extract_messages --project mwareeth --input-dirs mwareeth,examples --version 0.0.0  -o locales/mwareeth.pot

update-messages:
	uv run setup.py update_catalog -D mwareeth -i locales/mwareeth.pot -d locales/

compile-messages:
	uv run setup.py compile_catalog --directory locales/ -D mwareeth

translate: extract-messages update-messages compile-messages
