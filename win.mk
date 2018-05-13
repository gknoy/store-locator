#
# Windows for store-locator
#
# make -f win.mk prepare-venv
# make -f win.mk test
#

ENV:=env-win

# On Windows, virtualenv makes env/Scripts instead of env/bin
PIP=$(ENV)\\Scripts\\pip
PYTHON=$(ENV)\\Scripts\\python
FLAKE8=$(ENV)\\Scripts\\flake8
COVERAGE=$(ENV)\\Scripts\\coverage

prepare-venv:
	virtualenv $(ENV)
	$(PIP) install -r requirements.txt

lint:
	@$(FLAKE8) -vv --exclude=env,env-win --max-line-length=120

test: lint
	@$(COVERAGE) run -m unittest discover -s tests
	@echo ''
	@$(COVERAGE) report -m find_store.py
