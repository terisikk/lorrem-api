import markovify
import spacy


class POSifiedText(markovify.NewlineText):
    nlp = None

    def __init__(self, nlp, *args, **kwargs):
        self.nlp = nlp
        super().__init__(*args, **kwargs)

    def word_split(self, sentence):
        return ["::".join((word.text_with_ws, word.pos_)) for word in self.nlp(sentence)]

    def word_join(self, words):
        return "".join([word.split("::")[0] for word in words])


def create_generator(sentences):
    # Exclude stuff to not run some extra processing, might speed up a little
    nlp = spacy.load("fi_core_news_md", exclude=["ner", "textcat", "lemmatizer"])

    sentences = [construct_newline_sentence(document.sents) for document in nlp.pipe(sentences)]

    return POSifiedText(nlp, sentences, state_size=2, well_formed=False)


def construct_newline_sentence(sentences):
    return " ".join([sentence.text for sentence in sentences if len(sentence.text) > 1]) + "\n"
