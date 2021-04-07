.PHONY: init fmt check test build li run clean help

init:
	python3 -m pip install --upgrade pip
	pip install pipenv --upgrade
	PIPENV_VERBOSITY=-1 pipenv install --dev --pre

fmt:
	PIPENV_VERBOSITY=-1 pipenv run isort .
	PIPENV_VERBOSITY=-1 pipenv run black .

check: fmt
	PIPENV_VERBOSITY=-1 pipenv run flake8 --ignore=E501,W503 im
	PIPENV_VERBOSITY=-1 pipenv run bandit -r im
	PIPENV_VERBOSITY=-1 pipenv run black . --check
	PIPENV_VERBOSITY=-1 pipenv run mypy --config-file mypy.ini .

test:
	PIPENV_VERBOSITY=-1 pipenv run coverage run --source=im --omit=im/__version__.py -m pytest tests
	PIPENV_VERBOSITY=-1 pipenv run coverage report --fail-under=100 -m
	PIPENV_VERBOSITY=-1 pipenv run coverage xml

build: init fmt check clean test
	PIPENV_VERBOSITY=-1 pipenv run python setup.py sdist bdist_wheel

li: build
	pip install --editable .

run:
	PIPENV_VERBOSITY=-1 pipenv run python im/monitor.py

clean:
	rm -rf build dist .egg internet_monitor.egg-info .coverage coverage.xml im/__pycache__ .pytest_cache

help:
	@echo "This project assumes that you have python and pip installed."
	@echo "The following make targets are available:"
	@echo " init 	 		install all dependencies for dev env"
	@echo " check	 		check for flake8 syntax issues"
	@echo " test			run tests"
	@echo " build   		build your code and generate binaries to be published"
	@echo " publish-test		submit your code to pypi-test repository (requires .pypirc)"
	@echo " publish 		submit your code to pypi repository (requires .pypirc)"
	@echo " local-install 		Install im in editable mode (i.e. setuptools 'develop mode')"
	@echo " clean			cleanup your build"
	@echo " help			display this information"
