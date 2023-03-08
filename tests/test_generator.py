import re

from collections import namedtuple
from lorrem import generator


class MockLanguage(object):
    pass


def test_sentences_are_constructed_from_nlp():
    SentenceStub = namedtuple("SentenceStub", ["text"])

    sentences = [SentenceStub("This is a sentence."), SentenceStub("This, another sentence!")]
    expected = "This is a sentence. This, another sentence!\n"

    actual = generator.construct_newline_sentence(sentences)

    assert actual == expected


def test_POSifiedText_split_adds_tags():
    WordStub = namedtuple("WordStub", ["text_with_ws", "pos_"])

    # Mock nlp, using lambda to allow calling nlp() that normally requires loading a costly library.
    # Some trickery with split to get an approximation of spacy Doc.text_with_ws
    nlp = MockLanguage()
    nlp.__class__.__call__ = lambda self, sentence: [WordStub(word + ' ', "FAKE") for word in sentence.split(' ')[:-1]]

    markovgen = generator.POSifiedText(nlp, "Input Text")

    original = "This is a sentence. "
    expected = ["This ::FAKE", "is ::FAKE", "a ::FAKE", "sentence. ::FAKE"]

    actual = markovgen.word_split(original)

    assert actual == expected


def test_POSifiedText_join_returns_a_compiled_sentence():
    original = ["This ::FAKE", "is ::FAKE", "a ::FAKE", "sentence::FAKE", ".::FAKE"]
    expected = "This is a sentence."

    actual = generator.POSifiedText.word_join(None, original)
    
    assert actual == expected


def test_POSifiedText_join_handles_punctuation():
    original = ["This::FAKE", ", ::PUNCT", "a ::FAKE", "sentence::FAKE", ".::PUNCT"]
    expected = "This, a sentence."

    actual = generator.POSifiedText.word_join(None, original)
    
    assert actual == expected
