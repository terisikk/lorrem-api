import markovify
import requests
import spacy
import re

from flask import Flask, request
from config import cfg


QUOTE_API_TOKEN = cfg.get('quote_api_token')
HEADERS = {'Authorization': QUOTE_API_TOKEN}
QUERY = cfg.get('quote_api_query')
ROUTE = cfg.get('lorrem_api_route')
RATE_LIMIT = cfg.get('lorrem_api_limit')


def request_all_quotes():
    return requests.get(QUERY, headers=HEADERS).json()


def load_quotes():
    quotes = ""

    for quote in request_all_quotes():
        quotes += split_quote_to_sentences(quote["quote"])

    return quotes


# Approximation. Abbreviations etc. will also split currently.
def split_quote_to_sentences(quote):
    return '\n' + '\n'.join(re.split("[.!?]", quote))


def create_generator(text):
    nlp = spacy.load('fi_core_news_lg')
    quote_doc = nlp(text)

    quote_sents = get_nlp_sentences(quote_doc)

    return markovify.NewlineText(quote_sents, state_size=2)


def get_nlp_sentences(quote_doc):
    return ' '.join([sentence.text for sentence in quote_doc.sents if len(sentence.text) > 1])


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

quotes = load_quotes()
generator = create_generator(quotes)


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
