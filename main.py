import markovify
import requests
import spacy
import re

from flask import Flask
from config import cfg


QUOTE_API_TOKEN = cfg.get('quote_api_token')
HEADERS = {'Authorization': QUOTE_API_TOKEN}
QUERY = cfg.get('quote_api_query')
ROUTE = cfg.get('lorrem_api_route')


# https://towardsdatascience.com/text-generation-with-markov-chains-an-introduction-to-using-markovify-742e6680dc33
class POSifiedText(markovify.NewlineText):
    nlp = None

    def __init__(self, nlp, sentences, state_size):
        self.nlp = nlp
        super().__init__(sentences, state_size=state_size)

    def word_split(self, sentence):
        return ['::'.join((word.orth_, word.pos_)) for word in self.nlp(sentence)]

    def word_join(self, words):
        sentence = ' '.join(word.split('::')[0] for word in words)
        return sentence

    # Temporary fix for some weird spaces with special characters
    def make_sentence(self, tries):
        return super().make_sentence(tries=tries).replace(" ,", ",")


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

    return POSifiedText(nlp, quote_sents, 2)


def get_nlp_sentences(quote_doc):
    return ' '.join([sentence.text for sentence in quote_doc.sents if len(sentence.text) > 1])


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

quotes = load_quotes()
generator = create_generator(quotes)


@app.route(ROUTE)
def generate_sentence():
    return {"lorrem": generator.make_sentence(tries=50)}
