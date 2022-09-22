# Lorrem

A Finnish markov chain sentence generator microservice. Input to the generator should be passed by another REST API.

# How to run locally with docker

1. Create a custom config file based on the default.conf and add the api token and url of your input API
2. Build the docker image with dependencies with `docker build .`
3. Run the docker service with `docker run -e LORREM_CONFIG='conf/[custom-config.conf]' [sha-of-the-built-image]`
4. Test the service with curl: `docker exec -it [id-of-the-container] bash -c "curl -X GET http://127.0.0.1:5000/markovpy"`
