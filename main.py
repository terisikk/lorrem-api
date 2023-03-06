import markovify
import requests
import spacy
import re

from flask import Flask, request
from spacy.language import Language
from config import cfg


QUOTE_API_TOKEN = cfg.get('quote_api_token')
HEADERS = {'Authorization': QUOTE_API_TOKEN}
QUERY = cfg.get('quote_api_query')
ROUTE = cfg.get('lorrem_api_route')
RATE_LIMIT = cfg.get('lorrem_api_limit')


def request_all_quotes():
    return requests.get(QUERY, headers=HEADERS).json()


def load_quotes():
    return [quote["quote"] for quote in request_all_quotes()]


def create_generator(documents):
    # Exclude stuff to not run some extra processing, might speed up a little
    nlp = spacy.load('fi_core_news_md', exclude=["ner", "textcat", "lemmatizer"])

    sentences = [get_nlp_sentences(document) for document in nlp.pipe(documents)]

    class POSifiedText(markovify.NewlineText):
        def word_split(self, sentence):
            return ['::'.join((word.orth_, word.pos_)) for word in nlp(sentence)]

        # Yeeaaah a hack to get punctuation right
        def word_join(self, words):
            sentence = ""
            for word in words:
                parts = word.split('::')
                if parts[1] not in ["PUNCT"]:
                    sentence += ' '

                sentence += parts[0]

            return sentence.strip()

    return POSifiedText(sentences, state_size=2, well_formed=False)


def get_nlp_sentences(document):
    return ' '.join([sentence.text for sentence in document.sents if len(sentence.text) > 1]) + "\n"


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
