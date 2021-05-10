from app.utils import reverse


def test_reverse():
    assert reverse("abcde") == "edcba"