# Lorrem

A Finnish markov chain sentence generator microservice. Input to the generator should be passed by another REST API.

# Development

## Requirements
Requirements for running the application are listed in `requirements.txt`.
Extra requirements for dev environment are listed in `.devcontainer/requirements-dev.txt`

To run checks and tests, you need both. If you are using vscode devontainers, the requirements are automatically installed. 

## How to run in a devcontainer 

## Option 1: Using a fake backend

1. `LORREM_CONFIG=conf/dev.conf flask --app app run --host 0.0.0.0`
2. `curl -X GET http://127.0.0.1:5000/markovpy`

## Option 2: Using a real backend

1. Create a custom config file based on the default.conf and add the api token and url of your input API. Make sure `mode`is not set to dev. 
1. `LORREM_CONFIG=conf/[your-custom-conf].conf flask --app app run --host 0.0.0.0`
2. `curl -X GET http://127.0.0.1:5000/markovpy`

## How to run locally with docker

### Option 1: Using a fake backend
1. Build the docker image with dependencies with `docker build . -t lorrem:latest`
2. Run the docker service with `docker run --rm -e LORREM_CONFIG='conf/dev.conf' lorrem:latest`
3. Test the service with curl: `docker exec -it [id-of-the-container] bash -c "curl -X GET http://127.0.0.1:5000/markovpy"`

### Option 2: Using a real backend
1. Create a custom config file based on the default.conf and add the api token and url of your input API
2. Follow the instructions for fake backend, using your custom config file for env varaible `LORREM_CONFIG`


## How to run checks and tests

First drop into poetry shell with `poetry shell` OR prepend these commands with `poetry run`

* `ruff check .` to run static analysis
* `pytest` to run tests
* `coverage run` to run tests with coverage
* `coverage report` to get the coverage report
* `black .` to run autoformatting
