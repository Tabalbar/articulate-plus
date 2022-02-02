import json
import urllib.parse
import urllib.request

from nltk.corpus import wordnet

from .crawling_utils import CrawlingUtils
from ..text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils


class ResourceLookupUtils:
    @staticmethod
    def get_wordnet_synonyms(phrase, pos=wordnet.NOUN):
        if pos == 'PROPN' or pos == 'NOUN':
            pos = wordnet.NOUN
        if pos == 'VERB':
            pos = wordnet.VERB
        if pos == 'ADJ':
            pos = wordnet.ADJ
        if pos == 'ADV':
            pos = wordnet.ADV

        formatted = '_'.join(phrase.split())
        synsets = wordnet.synsets(formatted, pos)

        if len(synsets) == 0:
            return None

        synonyms = set()
        for synset in synsets:
            synonym = synset.name().split('.')[0]
            synonyms.add(urllib.parse.unquote(' '.join(synonym.split('_')).lower().replace('-', ' ')))

        lemmas = [lemma for lemma in [synset.lemmas() for synset in synsets][0]]
        for lemma in lemmas:
            synonyms.add(urllib.parse.unquote(' '.join(lemma.name().split('_')).lower().replace('-', ' ')))

        if len(synonyms) == 0:
            return None

        return synonyms

    HYPO = lambda s: s.hyponyms()

    @staticmethod
    def get_wordnet_hyponyms(phrase, pos=wordnet.NOUN):
        if pos == 'PROPN' or pos == 'NOUN':
            pos = wordnet.NOUN
        if pos == 'VERB':
            pos = wordnet.VERB
        if pos == 'ADJ':
            pos = wordnet.ADJ
        if pos == 'ADV':
            pos = wordnet.ADV

        formatted = '_'.join(phrase.split())
        if len(wordnet.synsets(formatted, pos)) == 0:
            return None

        synsets = [synset for synset in [list(synset.closure(ResourceLookupUtils.HYPO, depth=8)) for synset in
                                         wordnet.synsets(formatted, pos)]][0]

        if len(synsets) == 0:
            return None

        hyponyms = set()
        for synset in synsets:
            hyponym = synset.name().split('.')[0]
            hyponyms.add(urllib.parse.unquote(' '.join(hyponym.split('_')).lower().replace('-', ' ')))

        lemmas_for_synset = [synset.lemmas() for synset in synsets]

        for lemma_synset in lemmas_for_synset:
            for lemma in lemma_synset:
                hyponyms.add(urllib.parse.unquote(' '.join(lemma.name().split('_')).lower().replace('-', ' ')))

        if len(hyponyms) == 0:
            return None

        return hyponyms

    # example url: https://babelnet.io/v5/getSenses?lemma=bar%20chart&searchLang=EN&key=ed0f9a34-e565-49ad-ad2d-e3be7f6aaadd
    BABELNET_URL = 'https://babelnet.io/v5/getSenses?'
    BABELNET_LANGUAGE = 'EN'
    # BABELNET_KEY='ed0f9a34-e565-49ad-ad2d-e3be7f6aaadd'
    BABELNET_KEY = '7637b9fd-44c5-4e92-bc52-05db59b2d1d2'
    SEARCH_URL = BABELNET_URL + 'searchLang=' + BABELNET_LANGUAGE + '&key=' + BABELNET_KEY

    @staticmethod
    def get_babelnet_synonyms(phrase, include_novels=False, include_songs=False, pos='NOUN'):
        def is_phrase_about_novel(phrase):
            return 'novel' in phrase or 'thriller' in phrase or 'mystery' in phrase or 'fiction' in phrase or 'literature' in phrase

        def is_phrase_about_song(phrase):
            return 'song' in phrase

        search_query = ResourceLookupUtils.SEARCH_URL + '&pos=' + pos + '&lemma=' + urllib.parse.quote(phrase)
        search_results = CrawlingUtils.get_response_from_url(search_query)
        candidate_synonyms = json.loads(search_results.decode('utf-8'))

        synonyms = set()
        for synonym in candidate_synonyms:
            properties = synonym['properties']
            fullLemma = properties['fullLemma']
            simpleLemma = properties['simpleLemma']

            if include_novels == False and is_phrase_about_novel(fullLemma):
                continue
            if include_songs == False and is_phrase_about_song(fullLemma):
                continue
            # if TextProcessingUtils.does_phrase_contain_at_least_one_uppercase_word(fullLemma):
            #	continue
            if TextProcessingUtils.does_phrase_contain_at_least_two_uppercase_letters(fullLemma):
                continue
            synonyms.add(urllib.parse.unquote(' '.join(simpleLemma.split('_')).lower().replace('-', ' ')))

        if len(synonyms) == 0:
            return None

        return synonyms

    '''@staticmethod
    def process_wiki_dump(topics, output_text_file_name, wiki_dump_file_name = 'enwiki-latest_links.json.gz'):
        start_time = time.time()
        count_articles = 0

        cnt=0
        for line in smart_open(wiki_dump_file_name):
            article = json.loads(line)
            title = urllib.parse.unquote(article['title'].replace('_',' '))
            if title in topics:
                title = urllib.parse.unquote(article['title'].replace('_',' '))
                print("Found article " + title + " for including in " + output_text_file_name)
                for section_title, section_text in zip(article['section_titles'], article['section_texts']):
                    if section_text.startswith('<doc id='):
                        count_articles += 1
                        if count_articles % 2000 == 0:
                            elapsed_time = time.time() - start_time
                            print ('Processed article number:', count_articles, 'Elapsed time:', elapsed_time, 's')
                        continue
                    with open(output_text_file_name, 'a+') as f:
                        f.write(clean_text(text=section_text))
                        f.write('\n')
            cnt += 1
            print("Processed " + str(cnt) + " total wiki articles out of 5149501")

    @staticmethod
    def remove_wiki_subtitles(sent):
        processed_sent=[]
        index=0
        while index < len(sent):
            word = sent[index]
            if '===' not in word:
                processed_sent.append(word)
                index+=1
                continue
            index+=3
        return processed_sent'''
