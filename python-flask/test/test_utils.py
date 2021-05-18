from app.utils import reverse_sentence, generate_sentence


def test_reverse():
    assert reverse("abcde") == "edcba"


def test_random_sentence_generate():
    print(generate_sentence())