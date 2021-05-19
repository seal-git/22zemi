from app.utils import reverse_sentence, generate_sentence


def test_reverse_sentence():
    assert reverse_sentence("abcde") == "edcba"


def test_generate_sentence():
    print(generate_sentence())