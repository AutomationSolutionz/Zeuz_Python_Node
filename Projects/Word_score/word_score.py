from spellchecker import SpellChecker
from collections import Counter
from pathlib import Path
import json, os, sys, time
# Spell checker object, which should live throughout module lifespan
spell = SpellChecker()
import wordninja

import gzip, os, re
from math import log

en_path = str(Path(__file__).parent/'en.json')
wordninja_txt_path = str(Path(__file__).parent/'wordninja_words.txt')
dataset_path = str(Path(__file__).parent/'dataset.json')

dev_words = ["txt", "html", "css", "js"]
client_specific_words = ['ztad']
class LanguageModel(object):
    def __init__(self, word_file):
        # with open(en_path) as f:
        #     words = json.loads(f.read())
        # self._wordcost = {key: words[key] for key in sorted(self._wordcost,key=lambda x: self._wordcost[x], reverse=True)}

        with open(en_path) as f:
            words_spell = json.loads(f.read())
        with open(wordninja_txt_path) as f:
            words = f.read().split()
        # words = sorted(words,key=lambda x: words[x], reverse=True)
        # words = [i for i in words if i in words_spell]
        extra_words = [i for i in dev_words + client_specific_words if i not in words]
        words = words[:500] + extra_words + words[500:]
        self._wordcost = dict((k, log((i + 1) * log(len(words)))) for i, k in enumerate(words))
        self._maxword = max(len(x) for x in words)
        self._wordcost_keys = self._wordcost.keys()

        word_hash = {}
        words = sorted(words_spell,key=lambda x: words_spell[x], reverse=True)
        for word in words:
            sequence = word_hash
            for char in word:
                if char not in sequence:
                    sequence[char] = {}
                sequence = sequence[char]
            sequence['exists'] = True
        self._word_hash = word_hash
        print()

        words_spell = list(words_spell.keys())
        extra_words = [i for i in dev_words + client_specific_words if i not in words_spell]
        self._word_spell = words_spell[:500] + extra_words + words_spell[500:]

    def valid_word(self, word: str) -> bool:
        try:
            temp = self._word_hash
            for char in word:
                temp = temp[char]
            return temp['exists']
        except:
            return False

    def valid_word2(self, word: str) -> bool:
        idx = f"""['{"']['".join(word)}']['exists']"""
        try:
            eval(f"self._word_hash{idx}")
            return True
        except:
            return False

    def split(self, s):
        """Uses dynamic programming to infer the location of spaces in a string without spaces."""
        # Find the best match for the i first characters, assuming cost has
        # been built for the i-1 first characters.
        # Returns a pair (match_cost, match_length).
        def best_match(i):
            candidates = enumerate(reversed(cost[max(0, i - self._maxword):i]))
            return min((c + self._wordcost.get(s[i - k - 1:i].lower(), 9e999), k + 1) for k, c in candidates)

        # Build the cost array.
        cost = [0]
        for i in range(1, len(s) + 1):
            c, k = best_match(i)
            cost.append(c)

        # Backtrack to recover the minimal-cost string.
        out = []
        i = len(s)
        while i > 0:
            c, k = best_match(i)
            assert c == cost[i]
            # Apostrophe and digit handling (added by Genesys)
            newToken = True
            if not s[i - k:i] == "'":  # ignore a lone apostrophe
                if len(out) > 0:
                    # re-attach split 's and split digits
                    if out[-1] == "'s" or (s[i - 1].isdigit() and out[-1][0].isdigit()):  # digit followed by digit
                        out[-1] = s[i - k:i] + out[-1]  # combine current token with previous token
                        newToken = False
            # (End of Genesys addition)

            if newToken:
                out.append(s[i - k:i])

            i -= k

        return reversed(out)


DEFAULT_LANGUAGE_MODEL = LanguageModel(str(Path(__file__).parent/'wordninja_words.txt.gz'))
def split(s):
    return DEFAULT_LANGUAGE_MODEL.split(s)


def __word_score(split_attr_value):
    total_score = 0
    word_list = split_attr_value
    total_string_count = sum(len(i) for i in word_list)
    wrong_spell = spell.unknown(word_list)
    c1 = Counter(word_list)
    c2 = Counter(wrong_spell)
    diff = c1 - c2
    good_words = list(diff.elements())

    for each in good_words:
        total_score = total_score + ((len(each) / total_string_count) * 100)
    return round(total_score)


def prepare_dataset():
    import random
    words = DEFAULT_LANGUAGE_MODEL._wordcost.keys()
    dataset = []
    for i in range(2000):
        random_words = [random.choice(list(words)) for i in range(100)]
        sentence = "".join(random_words)
        dataset.append(sentence)
    with open(dataset_path, "w") as f:
        json.dump(dataset, f, indent=2)
    return dataset

def get_dataset():
    with open(dataset_path) as f:
        dataset = json.loads(f.read())
    return dataset
def partial_text_finder(text):
    w = split(text)
    # w = wordninja.split(text)
    ww = [i for i in w if DEFAULT_LANGUAGE_MODEL.valid_word2(i)]
    ww = list(set(ww))
    return ww
def partial_text_finder2(text):
    w = split(text)
    # w = wordninja.split(text)
    ww = [i for i in w if i in DEFAULT_LANGUAGE_MODEL._word_spell]
    return ww
def partial_text_finder3(text):
    w = split(text)
    ww = [i for i in w if DEFAULT_LANGUAGE_MODEL.valid_word(i)]
    ww = list(set(ww))
    return ww
def partial_text_finder4(text):
    w = split(text)
    ww = spell.known(w)
    ww = list(ww)
    return ww
def __split_words(raw_att_text):
    word_list = []
    # split by upper case words
    word_list_1 = __split_on_uppercase(raw_att_text, keep_contiguous=True)
    for each in word_list_1:
        # split by special char
        temp_list = re.split('[^a-zA-Z]', each)
        if len(temp_list) == 1:
            word_list.append(each)
        else:
            for each1 in temp_list:
                if each1 != '':
                    word_list.append(each1)
    word_list = [x.lower() for x in word_list]
    return word_list

def __split_on_uppercase(s, keep_contiguous=True):
    string_length = len(s)
    is_lower_around = (lambda: s[i - 1].islower() or
                               string_length > (i + 1) and
                               s[i + 1].islower())
    start = 0
    parts = []
    for i in range(1, string_length):
        if s[i].isupper() and (not keep_contiguous or is_lower_around()):
            parts.append(s[start: i])
            start = i
    parts.append(s[start:])
    return parts
if __name__ == "__main__":
    # dataset = prepare_dataset()
    dataset = get_dataset()

    text = "helloa_dsvNoisdh-voi hsd1soidn!v  "
    text = "usernametxtdevhtmlcssztadqa"
    text_ls = text.lower().strip()
    texts = __split_words(text)
    ninja_texts = []
    for t in texts:
        ninja_texts += partial_text_finder2(t)
    c = 0
    j = 0
    partial_words = []
    partial_word = ""
    while True:
        i = text_ls[c]
        if i in "_- ":
            partial_word += i
            c += 1
        elif i.isalpha() and j < len(ninja_texts) and ninja_texts[j] == text_ls[c:c+len(ninja_texts[j])]:
            partial_word += ninja_texts[j]
            c += len(ninja_texts[j])
            j += 1
        else:
            partial_word_strip = partial_word.strip().strip("-")
            if partial_word_strip:
                partial_words.append(partial_word_strip)
                partial_word = ""
            c += 1
        if c >= len(text_ls):
            partial_word_strip = partial_word.strip().strip("-")
            if partial_word_strip:
                partial_words.append(partial_word_strip)
            break

    # for i, partial_word in enumerate(partial_words):
    #     pass




    score = __word_score(["usernametext"])
    print(score)
    word_list = partial_text_finder2("h27&G87G5f7Creditvisionscore!h78g5238")
    # word_list = partial_text_finder("decarbonization")
    print(word_list)

    """ Bench Marking """
    s = time.perf_counter()
    for data in dataset:
        # print(data)
        word_list = partial_text_finder(data)
        # print(len(word_list), word_list)
    duration = time.perf_counter() - s
    print("\n\n------------ Finished --------------")
    print(duration, "sec\n\n")

    s = time.perf_counter()
    for data in dataset[:]:
        # print(data)
        word_list = partial_text_finder2(data)
        # print(len(word_list), word_list)
    duration = time.perf_counter() - s
    print("\n\n------------ Finished --------------")
    print(duration, "sec\n\n")

    s = time.perf_counter()
    for data in dataset[:]:
        # print(data)
        word_list = partial_text_finder3(data)
        # print(len(word_list), word_list)
    duration = time.perf_counter() - s
    print("\n\n------------ Finished --------------")
    print(duration, "sec\n\n")

    s = time.perf_counter()
    for data in dataset[:]:
        # print(data)
        word_list = partial_text_finder4(data)
        # print(len(word_list), word_list)
    duration = time.perf_counter() - s
    print("\n\n------------ Finished --------------")
    print(duration, "sec\n\n")

    print()