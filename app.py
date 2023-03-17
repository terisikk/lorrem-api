from flask import Flask, request
from lorrem import config, generator, quotes

import statistics

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

    sentences = []

    for _ in range(0, amount):
        if start:
            sentences.append(generator.make_sentence_with_start(start, False, test_output=None))
        else:
            sentences.append(generator.make_sentence(tries=50))

    return {"lorrem": sentences}


# This is for testing out the actual live generation and it's error rate
if __name__ == "__main__":
    nones = []

    [print(generator.make_sentence(strict=False, tries=50)) for _ in range(0, 10)]

    for i in range(0, 100):
        nones.append(list([generator.make_sentence(tries=50) for _ in range(0, 100)]).count(None))

    print("mean\t", statistics.mean(nones))
    print("max\t", max(nones))
    print("min\t", min(nones))
    print("mode\t", statistics.mode(nones))
