# Lorrem

A Finnish markov chain sentence generator microservice. Input to the generator should be passed by another REST API.

# Development

## Requirements
If you are using vscode devontainers, the requirements are *automatically installed*. 

If not, first, install `poetry` with `pipx install poetry==1.4.0`, then run `poetry install` to fetch the requirements listed in `pyproject.toml` / `poetry.lock`.

## How to run in a VSCode devcontainer 

## Option 1: Using a fake backend

1. `LORREM_CONFIG=conf/dev.conf make serve``
2. `curl -X GET http://127.0.0.1:5000/markovpy`

## Option 2: Using a real backend

1. Create a custom config file based on the default.conf and add the api token and url of your input API. Make sure `mode`is not set to dev. 
1. `LORREM_CONFIG=conf/[your-custom-conf].conf make serve`
2. `curl -X GET http://127.0.0.1:5000/markovpy`

## How to run checks and tests

First drop into poetry shell with `poetry shell` OR prepend these commands with `poetry run`

* `make lint` to run static analysis
* `make test` to run tests
* `make format` to run autoformatting
