import string
import os
import unidecode
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import *
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize


class TextProcessingUtils:
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    DOT_QUESTION_UNDERSCORE_HYPHEN = """!"#$%&()*+,/:;<=>@[\]^`{|}~"""
    HYPHEN = """!"#$%&()*+,/:;<=>@[\]^`{|}~.?"""

    STOPWORDS = set('for a of the in ok okay is was yeah yup sorry there way show see somewhere'.split())

    @staticmethod
    def stem(tokens):
        stemmed = []
        for token in tokens:
            stemmed.append(TextProcessingUtils.stemmer.stem(token))
        return stemmed

    @staticmethod
    def lemmatize(word, pos='n'):
        lemma = TextProcessingUtils.lemmatizer.lemmatize(word, pos=pos)
        return lemma

    @staticmethod
    def lemmatize_text(text, pos='n'):
        lemmatized = []
        for word in word_tokenize(text):
            lemmatized.append(TextProcessingUtils.lemmatizer.lemmatize(word, pos=pos))
        return ' '.join(lemmatized)

    @staticmethod
    def is_text_in_ascii(text):
        for c in text:
            if c not in string.ascii_letters and not c.isspace():
                return False
        return True

    @staticmethod
    def remove_punctuation(token, removeAllPunc="no -"):
        if "all" in removeAllPunc:
            return token.translate(None, string.punctuation)
        if "no -" in removeAllPunc:
            return token.translate(None, TextProcessingUtils.HYPHEN)
        if "no .?_-'" in removeAllPunc:
            return token.translate(None, TextProcessingUtils.DOT_QUESTION_UNDERSCORE_HYPHEN)

    @staticmethod
    def is_only_special_characters(s):
        if not re.match(r'^[_\W]+$', s):
            return True
        else:
            return False

    @staticmethod
    def is_date(string):
        try:
            parse(string)
            return True
        except Exception:
            return False

    @staticmethod
    def remove_file_if_exists(file_name):
        if os.path.exists(file_name):
            os.remove(file_name)
        else:
            print("The file " + file_name + " does not exist")

    @staticmethod
    def resolve_contractions(tokens):
        no_contractions = []
        index = 0
        for token in tokens:
            if token == "'s":
                if index - 1 >= 0 and tokens[index - 1] == 'let':
                    no_contractions.append('us')
                else:
                    no_contractions.append("is")
            elif token == "'m":
                no_contractions.append("am")
            elif token == "'d":
                no_contractions.append("would")
            elif token == "'ll":
                no_contractions.append("will")
            elif token == "n't":
                if index - 1 >= 0 and tokens[index - 1] == 'wo':
                    no_contractions[len(no_contractions) - 1] = 'will'
                if index - 1 >= 0 and tokens[index - 1] == 'ca':
                    no_contractions[len(no_contractions) - 1] = 'can'
                if index - 1 >= 0 and tokens[index - 1] == 'ai':
                    no_contractions[len(no_contractions) - 1] = 'am'
                no_contractions.append("not")
            elif token == "'ve":
                no_contractions.append("have")
            elif token == "'re":
                no_contractions.append("are")
            elif token == "'em":
                no_contractions.append("them")
            elif token == "na":
                if index - 1 >= 0 and tokens[index - 1] == 'gon':
                    no_contractions[len(no_contractions) - 1] = 'going'
                no_contractions.append('to')
            else:
                s = token.replace("'", "")
                if len(s) != 0:
                    no_contractions.append(s)
            index += 1
        return no_contractions

    @staticmethod
    def is_text_alphanumeric_without_character(text, character):
        # print("Is",text,"contain alpha numeric",character)
        for word in text.split(character):
            if len(word) == 0:
                continue
            if not word.isalnum():
                # print("FALSE NOT",word)
                return False
        # print("TRUE",text)
        return True

    @staticmethod
    def clean_text(text, mask_digits=False, filter_wiki_subtitles=False, use_lemmas=False, \
                   remove_stop_words=False, lowercase=False, resolve_contractions=True, \
                   remove_punctuation=False, remove_accents=True, remove_hyphens=False, \
                   remove_links=True):
        text = text.strip()

        if remove_accents:
            text = unidecode.unidecode(text)

        if lowercase:
            text = text.lower()

        text = re.sub('\\*(.*?)\\*', '', text)
        text = re.sub('\\[(.*?)\\]', '', text)
        text = re.sub('[a-zA-Z0-9]*.img', '', text)
        text = re.sub('\\<(.*?)\\>', '', text)

        if mask_digits:
            text = re.sub('\d', '0', text)

        if remove_links:
            text = re.sub('(www|http|.com|.edu|.org|.gov|.net)\S+', '', text)
            text = re.sub('(www|http|.com|.edu|.org|.gov|.net)\S+ ', '', text)

        if remove_hyphens:
            text = text.replace('-', ' ')

        if remove_punctuation:
            span = re.search('^-*', text).span()
            if len(span) > 0:
                end = span[1]
                # print("TEXT",text,"END",end,"FINAL",text[end:])
                text = text[end:]

        sents = [word_tokenize(sent) for sent in sent_tokenize(text)]
        result = ''
        for sent in sents:
            if resolve_contractions:
                processed_sent = TextProcessingUtils.resolve_contractions(sent)

            if filter_wiki_subtitles:
                processed_sent = TextProcessingUtils.remove_wiki_subtitles(processed_sent)

            processed_sent_norm = []
            for word in processed_sent:
                processed_word = word
                # print("processing word",processed_word)
                if use_lemmas:
                    processed_word = TextProcessingUtils.lemmatize(processed_word)

                if word.isalnum():
                    word = word.replace("'", "")
                    if use_lemmas == True:
                        processed_word = TextProcessingUtils.lemmatize(word)
                    processed_sent_norm.append(processed_word)
                    # print("found alnum",processed_word)
                    continue

                if remove_hyphens == False and "-" in word:
                    processed_sent_norm.append(processed_word)
                    continue

                if '_' in word:
                    processed_sent_norm.append(processed_word)

                if remove_punctuation and 'png' not in processed_word.lower():
                    # print("remove punc",processed_word)
                    continue

                if "?" in word and TextProcessingUtils.is_text_alphanumeric_without_character(text=word, character="?"):
                    processed_sent_norm.append(processed_word)
                    continue

                elif "." in word and TextProcessingUtils.is_text_alphanumeric_without_character(text=word,
                                                                                                character="."):
                    processed_sent_norm.append(processed_word)
                    continue

                elif "!" in word and TextProcessingUtils.is_text_alphanumeric_without_character(text=word,
                                                                                                character="!"):
                    processed_sent_norm.append(processed_word)

            for index in range(len(processed_sent_norm)):
                token = processed_sent_norm[index]

                if index + 1 >= len(processed_sent_norm):
                    result += token + " "
                    continue

                if remove_punctuation:
                    result += token + " "
                    continue

                next_token = processed_sent_norm[index + 1]
                if next_token == "?" or next_token == "." or next_token == "!":
                    result += token
                    continue

                result += token + " "

            result = result[:-1] + "\n"
        result = result[:-1]
        if remove_stop_words == True:
            result = TextProcessingUtils.remove_stop_words(result)
        return result.strip()

    @staticmethod
    def does_phrase_contain_at_least_two_uppercase_letters(phrase):
        capital_letters = re.findall('[A-Z]', phrase)
        if len(capital_letters) == 0:
            return False
        if len(capital_letters) == 1:
            return False
        return True

    @staticmethod
    def does_phrase_contain_at_least_one_uppercase_word(phrase):
        for word in phrase.split('_'):
            if word == word.upper():
                return True

    @staticmethod
    def remove_repeated_words_from_beginning(text):
        tokens = text.split()

        if len(tokens) == 1:
            return ' '.join(tokens)

        repeated_word = tokens[1]
        repeated_index = 0
        for index in range(2, len(tokens)):
            if tokens[index] == repeated_word:
                repeated_index = index

        tokens = tokens[repeated_index:]
        return ' '.join(tokens)

    def remove_stop_words(text):
        return ' '.join([word for word in word_tokenize(text) if word not in TextProcessingUtils.STOPWORDS])

    @staticmethod
    def remove_wiki_subtitles(tokens):
        processed_sent = []
        index = 0
        while index < len(tokens):
            word = tokens[index]
            if '===' not in word:
                processed_sent.append(word)
                index += 1
                continue
            index += 3
        return processed_sent
