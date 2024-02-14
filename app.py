import time

from flask import Flask, request

from lorrem import config, generator, quotes

ROUTE = config.cfg.get("lorrem_api_route")
RATE_LIMIT = config.cfg.get("lorrem_api_limit")

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

documents = quotes.load_quotes()
generator = generator.create_generator(documents)


@app.route(ROUTE)
def generate_sentence():
    amount = 1

    try:
        amount_arg = request.args.get("amount")
        start = request.args.get("start")

        if amount_arg is not None:
            amount = int(amount_arg)
    except (ValueError, TypeError):
        return "Validation error", 400

    if amount > RATE_LIMIT:
        return "Too many requests", 429

    sentences = set()

    for _ in range(0, amount):
        if start:
            sentences.add(generator.make_sentence_with_start(start, strict=False, test_output=None))
        else:
            sentences.add(generator.make_sentence(tries=50))

    return {"lorrem": list(sentences)}


# This is for testing out the actual live generation and it's error rate
if __name__ == "__main__":
    nones = []

    sentences = set()

    start = time.time()
    for _ in range(0, 1000):
        sentences.add(
            generator.make_sentence_with_start("owo nya", strict=False, tries=50, test_output=None)
        )
    print(time.time() - start)
