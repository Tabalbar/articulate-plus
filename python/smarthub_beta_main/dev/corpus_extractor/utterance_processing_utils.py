import re
import string


class UtteranceProcessingUtils:
    # ex: 5-2.png
    HYPHEN_DIGITS = re.compile('\\d{1,2}-\\d{1,2}(.png)?')

    # ex: x-axis
    AXIS_MENTIONS = re.compile('[a-z]+-(axis)')

    @staticmethod
    def remove_pauses(utterance):
        tokens = utterance.split()
        index = 0
        tokens_without_pauses = []
        while index < len(tokens):
            if index + 1 >= len(tokens) and '--' not in tokens[index]:
                tokens_without_pauses.append(tokens[index])
                index += 1
                continue
            if index + 1 < len(tokens) and '--' in tokens[index + 1]:
                index += 2
                continue
            tokens_without_pauses.append(tokens[index])
            index += 1
        return ' '.join(tokens_without_pauses)

    @staticmethod
    def remove_hyphens_from_word(utterance_word):
        if '-' not in utterance_word:
            return utterance_word
        if re.search(UtteranceProcessingUtils.HYPHEN_DIGITS, utterance_word.lower()) is not None:
            return utterance_word
        if re.search(UtteranceProcessingUtils.AXIS_MENTIONS, utterance_word.lower()) is not None:
            return utterance_word
        return utterance_word.replace('-', ' ')

    @staticmethod
    def remove_hyphens(utterance):
        return ' '.join([UtteranceProcessingUtils.remove_hyphens_from_word(word) for word in utterance.split()])

    @staticmethod
    def remove_abbreviation_underscores(utterance):
        return utterance.replace('_', '')

    @staticmethod
    def remove_unknown_terms(utterance):
        return utterance.replace('xxx ', '').replace(' xxx', '').replace('Xxx ', '').replace('xxx', ''). \
            replace('XXX', '')

    @staticmethod
    def replace_noon_and_midnight(utterance):
        if '12' not in utterance:
            utterance = re.sub(' noon', ' 12 noon', utterance)
            utterance = re.sub(' midnight', ' 12 midnight', utterance)
        return utterance

    @staticmethod
    def fix_formatting(utterance):
        utterance = utterance.replace('\n', ' ')
        utterance = utterance.replace(' .', '')
        if utterance.strip() in string.punctuation:
            utterance = ''
        return utterance

    @staticmethod
    def clean_utterance(utterance, remove_pauses=True, remove_abbreviation_underscores=True,
                        remove_unknown_terms=True, remove_hyphens=False, replace_noon_and_midnight=True,
                        remove_new_lines=True):
        if remove_pauses:
            utterance = UtteranceProcessingUtils.remove_pauses(utterance)
        if remove_abbreviation_underscores:
            utterance = UtteranceProcessingUtils.remove_abbreviation_underscores(utterance)
        if remove_unknown_terms:
            utterance = UtteranceProcessingUtils.remove_unknown_terms(utterance)
        if remove_hyphens:
            utterance = UtteranceProcessingUtils.remove_hyphens(utterance)
        if replace_noon_and_midnight:
            utterance = UtteranceProcessingUtils.replace_noon_and_midnight(utterance)
        if remove_new_lines:
            utterance = UtteranceProcessingUtils.fix_formatting(utterance)

        return utterance
