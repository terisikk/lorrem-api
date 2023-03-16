import markovify
import spacy


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
        super().__init__(input_text, state_size, chain, parsed_sentences, retain_original, well_formed, reject_reg)

    def generate_corpus(self, texts):
        if not self.nlp:
            self.nlp = spacy.load("fi_core_news_md", exclude=["ner", "textcat", "lemmatizer", "entity_linker"])
            self.nlp.replace_pipe("parser", "newlinesentencizer")

        runs = []

        for doc in self.nlp.pipe(texts):
            runs += map(self.word_split, filter(self.test_sentence_input, doc.sents))

        return runs

    def test_sentence_input(self, sentence):
        if len(sentence.text.strip()) == 0:
            return False

        return True

    def word_split(self, sentence):
        return ["::".join((word.text_with_ws, word.pos_)) for word in sentence]

    def word_join(self, words):
        return "".join([word.split("::")[0] for word in words])

    def test_sentence_output(self, words, max_overlap_ratio, max_overlap_total):
        # Override sanity check in dev environment, and just return any generated sentence
        if MODE == "dev":
            return True

        return super().test_sentence_output(words, max_overlap_ratio, max_overlap_total)


def create_generator(texts):
    return POSifiedText(texts, state_size=2, well_formed=False)


# Usage as a decorator
@spacy.Language.factory(
    "newlinesentencizer",
    assigns=["token.is_sent_start", "doc.sents"],
)
def make_newline_sentencizer(nlp, name):
    return spacy.pipeline.Sentencizer(punct_chars=["\n"])
