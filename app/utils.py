from essential_generators import DocumentGenerator


def reverse_sentence(s):
    result = ""
    for i in range(len(s)):
        result += s[len(s) - i - 1]
    return result


def generate_sentence():
    gen = DocumentGenerator()
    return gen.sentence()