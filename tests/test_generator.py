from collections import namedtuple

import spacy

from lorrem import generator


class MockLanguage(object):
    error_handler = None

    # Mock nlp to allow calling nlp() that normally requires loading a costly library.
    # Some trickery with split to get an approximation of spacy Doc.text_with_ws
    def __call__(self, text):
        ret = None

        try:
            words = text.split(" ")
            vocab = spacy.vocab.Vocab(string=words)
            spaces = [True] * (len(words) - 1) + [False]
            pos = ["X"] * (len(words))
            sent_starts = [True] + (len(words) - 1) * [False]
            ret = spacy.tokens.Doc(vocab, words, spaces, pos=pos, sent_starts=sent_starts)
        except Exception as e:
            if self.error_handler:
                self.error_handler("Fake", "Fake", None, e)

        return ret

    def pipe(self, texts):
        return [self.__class__.__call__(self, text) for text in texts]

    def replace_pipe(self, *args, **kwargs):
        pass

    def set_error_handler(self, handler):
        self.error_handler = handler


def test_sentences_are_constructed_from_nlp():
    language = MockLanguage()

    markovgen = generator.POSifiedText(["Input Text"], nlp=language)

    original = ["This is a sentence.", "This is another sentence."]

    actual = list(markovgen.generate_corpus(original))
    expected = [
        ["This ::X", "is ::X", "a ::X", "sentence.::X"],
        ["This ::X", "is ::X", "another ::X", "sentence.::X"],
    ]

    assert actual == expected


def test_corpus_generation_does_not_fail_with_empty_text():
    language = MockLanguage()
    language.set_error_handler(generator.nlp_skip_errors)

    generator.POSifiedText(["Input text", "", "test"], nlp=language)


def test_POSifiedText_split_adds_tags():
    nlp = MockLanguage()

    markovgen = generator.POSifiedText(["Input Text"], nlp=nlp)

    original = list(markovgen.nlp("This is a sentence.").sents)[0]
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
    markovgen = generator.POSifiedText(["Input Text"], nlp=nlp)

    actual = markovgen.test_sentence_output([], 1, 1)

    assert not actual


def test_generator_test_sentece_output_in_debug_mode_is_true(monkeypatch):
    monkeypatch.setattr(generator, "MODE", "dev")

    nlp = MockLanguage()
    markovgen = generator.POSifiedText(["Input Text"], nlp=nlp)

    actual = markovgen.test_sentence_output([], 1, 1)

    assert actual is True


def test_space_sentencizer_factory_works():
    actual = generator.make_newline_sentencizer(None, "test")

    assert type(actual) == spacy.pipeline.Sentencizer
    assert "\n" in actual.punct_chars
    assert len(actual.punct_chars) == 1


def test_sentence_input_test_dismisses_empty_sentences():
    Sentence = namedtuple("Sentence", ["text"])

    original = [
        Sentence("Test sentence"),
        Sentence("   "),
        Sentence(""),
        Sentence("This is a test   "),
    ]
    expected = [Sentence("Test sentence"), Sentence("This is a test   ")]

    nlp = MockLanguage()
    markovgen = generator.POSifiedText(["Input Text"], nlp=nlp)

    actual = list(filter(markovgen.test_sentence_input, original))

    assert actual == expected
    assert len(expected) == 2


def test_make_sentence_with_start_works(monkeypatch):
    monkeypatch.setattr(generator, "MODE", "dev")

    nlp = MockLanguage()

    gen_input = ["Ystävän poika leikkii.", "Naapurin poika nukkuu.", "Metsän poika vonkuu."]

    markovgen = generator.POSifiedText(gen_input, nlp=nlp)

    actual = markovgen.make_sentence_with_start("Naapurin", strict=False)

    assert actual.startswith("Naapurin")


def test_make_sentence_is_case_insentive(monkeypatch):
    monkeypatch.setattr(generator, "MODE", "dev")

    nlp = MockLanguage()

    gen_input = ["YSTÄVÄN POIKA LEIKKII.", "NAAPURIN POIKA NUKKUU.", "METSÄN POIKA VONKUU."]

    markovgen = generator.POSifiedText(gen_input, nlp=nlp)

    actual = markovgen.make_sentence_with_start("naapurin", strict=False)

    assert actual.startswith("NAAPURIN")


def test_make_sentence_with_start_works_when_beginning_eq_state_size(monkeypatch):
    monkeypatch.setattr(generator, "MODE", "dev")

    nlp = MockLanguage()

    gen_input = ["Ystävän poika leikkii.", "Naapurin poika nukkuu.", "Metsän poika vonkuu."]

    markovgen = generator.POSifiedText(gen_input, nlp=nlp, state_size=2)

    actual = markovgen.make_sentence_with_start("Naapurin poika", strict=False, test_output=False)

    assert actual and actual.startswith("Naapurin poika")


def test_make_sentence_with_start_prepends_overflow_with_long_state(monkeypatch):
    monkeypatch.setattr(generator, "MODE", "dev")

    nlp = MockLanguage()

    gen_input = ["Ystävän poika leikkii.", "Naapurin poika nukkuu.", "Metsän poika vonkuu."]

    markovgen = generator.POSifiedText(gen_input, nlp=nlp, state_size=1)

    actual = markovgen.make_sentence_with_start("Petterin poika", strict=False, test_output=False)

    assert actual and actual.startswith("Petterin poika")


def test_make_sentence_with_start_overflow_does_not_add_extra_spaces(monkeypatch):
    monkeypatch.setattr(generator, "MODE", "dev")

    nlp = MockLanguage()

    gen_input = ["Ystävän poika leikkii.", "Naapurin poika nukkuu.", "Metsän poika vonkuu."]

    markovgen = generator.POSifiedText(gen_input, nlp=nlp, state_size=1)

    actual = markovgen.make_sentence_with_start("Petteri, poika", strict=False, test_output=False)

    assert actual and actual.startswith("Petteri, poika")


def test_make_sentence_with_start_does_not_error_out_when_no_key_found(monkeypatch):
    monkeypatch.setattr(generator, "MODE", "dev")

    nlp = MockLanguage()

    gen_input = ["Fake input"]

    markovgen = generator.POSifiedText(gen_input, nlp=nlp, state_size=1)

    actual = markovgen.make_sentence_with_start("Test", strict=False, test_output=False)

    assert not actual


def test_make_sentence_with_start_returns_none_with_empty_start(monkeypatch):
    monkeypatch.setattr(generator, "MODE", "dev")

    nlp = MockLanguage()

    gen_input = ["Fake input"]

    markovgen = generator.POSifiedText(gen_input, nlp=nlp, state_size=1)

    actual = markovgen.make_sentence_with_start("", strict=False, test_output=False)

    assert not actual
