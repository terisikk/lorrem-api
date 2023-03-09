# Lorrem

A Finnish markov chain sentence generator microservice. Input to the generator should be passed by another REST API.

# Development

## Requirements
Requirements for running the application are listed in `requirements.txt`.
Extra requirements for dev environment are listed in `.devcontainer/requirements-dev.txt`

To run checks and tests, you need both. If you are using vscode devontainers, the requirements are automatically installed. 

## How to run locally with docker

1. Create a custom config file based on the default.conf and add the api token and url of your input API
2. Build the docker image with dependencies with `docker build . -t lorrem:latest`
3. Run the docker service with `docker run --rm -e LORREM_CONFIG='conf/[custom-config.conf]' lorrem:latest`
4. Test the service with curl: `docker exec -it [id-of-the-container] bash -c "curl -X GET http://127.0.0.1:5000/markovpy"`

## How to run checks and tests

* `ruff check .` to run static analysis
* `pytest` to run tests
* `coverage run` to run tests with coverage
* `coverage report` to get the coverage report
* `black .` to run autoformatting
