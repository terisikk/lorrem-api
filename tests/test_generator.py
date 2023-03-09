import spacy

from collections import namedtuple
from lorrem import generator


class MockLanguage(object):
    # Mock nlp to allow calling nlp() that normally requires loading a costly library.
    # Some trickery with split to get an approximation of spacy Doc.text_with_ws
    def __call__(self, text):
        words = text.split(" ")
        vocab = spacy.vocab.Vocab(string=words)
        spaces = [True] * (len(words) - 1) + [False]
        pos = ["X"] * (len(words))
        sent_starts = [True] + (len(words) - 1) * [False]

        return spacy.tokens.Doc(vocab, words, spaces, pos=pos, sent_starts=sent_starts)

    def pipe(self, texts):
        return [self.__class__.__call__(self, text) for text in texts]


SentenceStub = namedtuple("SentenceStub", ["text_with_ws"])


def test_sentences_are_constructed_from_nlp():
    sentences = [
        SentenceStub("This is a sentence. "),
        SentenceStub("This, another sentence!"),
    ]

    expected = "This is a sentence. This, another sentence!\n"
    actual = generator.construct_newline_sentence(sentences)

    assert actual == expected


def test_POSifiedText_split_adds_tags():
    nlp = MockLanguage()

    markovgen = generator.POSifiedText(nlp, "Input Text")

    original = "This is a sentence."
    expected = ["This ::X", "is ::X", "a ::X", "sentence.::X"]
    actual = markovgen.word_split(original)

    assert actual == expected


def test_POSifiedText_join_returns_a_compiled_sentence():
    original = ["This ::X", "is ::X", "a ::X", "sentence::X", ".::X"]
    expected = "This is a sentence."
    actual = generator.POSifiedText.word_join(None, original)

    assert actual == expected


def test_POSifiedText_join_handles_punctuation():
    original = ["This::X", ", ::PUNCT", "a ::X", "sentence::X", ".::PUNCT"]
    expected = "This, a sentence."
    actual = generator.POSifiedText.word_join(None, original)

    assert actual == expected


def test_generator_is_created(monkeypatch):
    original = ["This is a sentence.", "This, also a sentence!"]
    expected = generator.POSifiedText

    def mock_load(name, *args, **kwargs):
        nlp = MockLanguage()
        return nlp

    monkeypatch.setattr(spacy, "load", mock_load)

    actual = generator.create_generator(original)

    assert actual.__class__ == expected
    assert actual.nlp is not None


def test_generator_test_sentence_output():
    nlp = MockLanguage()
    markovgen = generator.POSifiedText(nlp, "Input Text")

    actual = markovgen.test_sentence_output([], 1, 1)

    assert not actual


def test_generator_test_sentece_output_in_debug_mode_is_true(monkeypatch):
    monkeypatch.setattr(generator, "MODE", "dev")

    nlp = MockLanguage()
    markovgen = generator.POSifiedText(nlp, "Input Text")

    actual = markovgen.test_sentence_output([], 1, 1)

    assert actual == True
