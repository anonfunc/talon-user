import string

from talon.voice import Str

mapping = {"semicolon": ";", "new-line": "\n", "new-paragraph": "\n\n"}
punctuation = set(".,-!?")
vocab = ["nonce"]


def parse_word(w):
    w = str(w).lstrip("\\").split("\\", 1)[0]
    w = mapping.get(w, w)
    # w = w.replace("-", "")  # hate dragon hyphenation.
    return w


def parse_words(m):
    try:
        # noinspection PyProtectedMember
        return list(map(parse_word, m.dgndictation[0]._words))
    except AttributeError:
        return []


def join_words(words, sep=" "):
    out = ""
    for i, w in enumerate(words):
        if i > 0 and w not in punctuation:
            out += sep
        out += w
    return out


def insert(s):
    Str(s)(None)


def text(m):
    insert(join_words(parse_words(m)))


def word(m):
    try:
        # noinspection PyProtectedMember
        insert(join_words(list(map(parse_word, m.dgnwords[0]._words))))
    except AttributeError:
        pass


def surround(by):
    def func(i, w, last):
        if i == 0:
            w = by + w
        if last:
            w += by
        return w

    return func


def rot13(_, w, __):
    out = ""
    for c in w.lower():
        if c in string.ascii_lowercase:
            c = chr((((ord(c) - ord("a")) + 13) % 26) + ord("a"))
        out += c
    return out


numeral_map = dict((str(n), n) for n in range(0, 20))
for n in range(20, 101, 10):
    numeral_map[str(n)] = n
for n in range(100, 1001, 100):
    numeral_map[str(n)] = n
for n in range(1000, 10001, 1000):
    numeral_map[str(n)] = n
numeral_map["oh"] = 0  # synonym for zero
numeral_map["and"] = None  # drop me

numerals = " (" + " | ".join(sorted(numeral_map.keys())) + ")+"
optional_numerals = " (" + " | ".join(sorted(numeral_map.keys())) + ")*"


def text_to_number(words):
    tmp = [str(s).lower() for s in words]
    words = [parse_word(w) for w in tmp]

    result = 0
    factor = 1
    for w in reversed(words):
        # print("{} {} {}".format(result, factor, w))
        if w not in numerals:
            raise Exception("not a number: {}".format(words))

        number = numeral_map[w]
        if number is None:
            continue

        number = int(number)
        if number > 10:
            result = result + number
        else:
            result = result + factor * number
        factor = (10 ** len(str(number))) * factor
    return result


def text_to_range(words, delimiter="until"):
    tmp = [str(s).lower() for s in words]
    split = tmp.index(delimiter)
    start = text_to_number(words[:split])
    end = text_to_number(words[split + 1 :])
    return start, end
