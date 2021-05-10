import re


def reverse(s):
    result = ""
    for i in range(len(s)):
        result += s[len(s) - i - 1]
    return result
