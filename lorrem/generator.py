import functools
import random

import markovify
import spacy
from markovify.chain import BEGIN

from .config import cfg

MODE = cfg.get("mode", None)


class POSifiedText(markovify.NewlineText):
    nlp = None

    def __init__(
        self,
        input_text,
        state_size=2,
        chain=None,
        parsed_sentences=None,
        retain_original=True,
        well_formed=True,
        reject_reg="",
        nlp=None,
    ):
        self.nlp = nlp
        super().__init__(
            input_text,
            state_size,
            chain,
            parsed_sentences,
            retain_original,
            well_formed,
            reject_reg,
        )

    def generate_corpus(self, texts):
        if not self.nlp:
            self.nlp = spacy.load(
                "fi_core_news_md", exclude=["ner", "textcat", "lemmatizer", "entity_linker"]
            )
            self.nlp.replace_pipe("parser", "newlinesentencizer")
            self.nlp.set_error_handler(nlp_skip_errors)

        runs = []

        for doc in self.nlp.pipe(texts):
            if doc:
                runs += map(self.word_split, filter(self.test_sentence_input, doc.sents))

        return runs

    def test_sentence_input(self, sentence):
        return len(sentence.text.strip()) > 0

    def word_split(self, sentence):
        return ["::".join((word.text_with_ws, word.pos_)) for word in sentence]

    def word_join(self, words):
        return "".join([word.split("::")[0] for word in words])

    def test_sentence_output(self, words, max_overlap_ratio, max_overlap_total):
        # Override sanity check in dev environment, and just return any generated sentence
        if MODE == "dev":
            return True

        return super().test_sentence_output(words, max_overlap_ratio, max_overlap_total)

    def make_sentence_with_start(self, beginning, **kwargs):
        doc = self.nlp(beginning)

        if not doc:
            return None

        beginning = tuple(token.text.lower() for token in doc)

        starting_words = []
        starting_words = beginning[self.state_size * -1 :]

        init_states = self.get_init_states(starting_words)
        random.shuffle(init_states)

        for init_state in init_states:
            output = self.make_sentence(init_state, **kwargs)

            if len(beginning) > self.state_size:
                return str(doc[: -1 * self.state_size]) + " " + output
            else:
                return output

    @functools.lru_cache(maxsize=128)  # noqa
    def get_init_states(self, beginning):
        word_count = len(beginning)
        return [
            key
            for key in self.chain.model.keys()
            # check for starting with begin as well ordered lists
            if tuple(k.split("::")[0].strip().lower() for k in filter(lambda x: x != BEGIN, key))[
                :word_count
            ]
            == beginning
        ]


def create_generator(texts):
    return POSifiedText(texts, state_size=2, well_formed=False)


@spacy.Language.factory(
    "newlinesentencizer",
    assigns=["token.is_sent_start", "doc.sents"],
)
def make_newline_sentencizer(nlp, name):
    return spacy.pipeline.Sentencizer(punct_chars=["\n"])


def nlp_skip_errors(proc_name, proc, docs, e):
    print(f"An error occurred when applying component {proc_name}: {e}, continuing processing.")
