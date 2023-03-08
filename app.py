from flask import Flask, request
from lorrem import config, generator, quotes


ROUTE = config.cfg.get('lorrem_api_route')
RATE_LIMIT = config.cfg.get('lorrem_api_limit')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

documents = quotes.load_quotes()
generator = generator.create_generator(documents)


@app.route(ROUTE)
def generate_sentence():
    amount = 1

    try:
        amount_arg = request.args.get("amount")

        if amount_arg is not None:
            amount = int(amount_arg)
    except (ValueError, TypeError):
        return "Validation error", 400

    if amount > RATE_LIMIT:
        return "Too many requests", 429

    return {"lorrem": [generator.make_sentence(tries=50) for _ in range(0, amount)]}
