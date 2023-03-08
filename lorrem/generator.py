import markovify
import spacy


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
