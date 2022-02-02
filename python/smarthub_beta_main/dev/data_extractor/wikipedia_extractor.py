import json
import multiprocessing
import os
import os.path
from difflib import SequenceMatcher
from functools import partial

import numpy as np
import whoosh.index as index
from smart_open import smart_open
from whoosh import scoring
from whoosh.fields import *
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

from .extractor import Extractor
from .processing_utils import ProcessingUtils
from ..text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils


class WikipediaExtractor(Extractor):
    def __init__(self, input_source_file, topics, index_path, output_target_file):
        super().__init__(input_source_file, output_target_file, None)
        self.topics = [TextProcessingUtils.clean_text( \
            text=topic, use_lemmas=True, remove_stop_words=True, lowercase=True) \
            for topic in topics]

        self.index_path = index_path
        self.entities = set()

    @staticmethod
    def search_index(search_text, searcher, query_processor):
        search_results = searcher.search(query_processor.parse(search_text), limit=10)
        if len(search_results) == 0:
            return None, None
        best_title_match = search_results[np.argmax(np.asarray(
            [SequenceMatcher(None, search_text, search_result['title']).ratio() for search_result in search_results]))]
        return best_title_match['links'], best_title_match['content']

    def extract_text_from_topics(self, topics):
        print("Started process " + str(multiprocessing.current_process()) + \
              " on " + str(len(topics)) + " total topics")

        ix = index.open_dir(self.index_path)
        query_processor = QueryParser("title", schema=ix.schema)
        searcher = ix.searcher(weighting=scoring.BM25F())

        text = ""
        counts = 0
        links = set()
        for topic in topics:
            links0, text0 = WikipediaExtractor.search_index(search_text=topic, searcher=searcher,
                                                            query_processor=query_processor)
            if text0 is None:
                continue
            text += text0 + "\n"
            links.update(set(links0))

            for link0 in links0:
                links1, text1 = WikipediaExtractor.search_index(search_text=link0, searcher=searcher,
                                                                query_processor=query_processor)
                if text1 is None:
                    continue
                text += text1 + "\n"
                links.update(set(links1))


            counts += 1
            print(str(multiprocessing.current_process()) + " completed processing " + \
                  str(counts) + " topics out of " + str(len(topics)))

        print("Completed process " + str(multiprocessing.current_process()) + \
              " on " + str(len(topics)) + " total topics")

        return text, links

    def extract(self):
        no_of_processes = 4
        work_chunks = ProcessingUtils.slice_work_chunks(work_per_process=20, iterable=self.topics)
        pool = multiprocessing.Pool(processes=no_of_processes)

        func = partial(self.extract_text_from_topics)
        for text, links in pool.imap_unordered(func, work_chunks, chunksize=1):
            print("text from process " + str(multiprocessing.current_process()) + \
                  " has length " + str(len(text)))

            if text is None:
                continue

            with open(self.output_target_file, 'a+') as f:
                f.write(text + "\n")

            self.entities.update(set(links))

            print("text from process " + str(multiprocessing.current_process()) + \
                  " with length " + str(len(text)) + " and total links " + str(
                len(links)) + " has completed writing to disk")
            del text
            del links

        print("Closing pool")
        pool.close()

        print("Joining pool")
        pool.join()

    def index_by_article_titles(self):
        schema = Schema(title=TEXT(stored=True), content=STORED, links=STORED)
        if not os.path.exists(self.index_path):
            os.mkdir(self.index_path)

        ix = create_in(self.index_path, schema)
        ix = open_dir(self.index_path)

        writer = ix.writer(limitmb=4096, procs=12, multisegment=True)
        counts = 0
        for line in smart_open(self.input_source_file):
            article = json.loads(line)
            title = article['title']

            title = TextProcessingUtils.clean_text(text=title, use_lemmas=True, remove_stop_words=True, lowercase=True)
            text = ''
            for section_title, section_text in zip(article['section_titles'], article['section_texts']):
                if section_text.startswith('<doc id='):
                    continue
                text += TextProcessingUtils.clean_text(text=section_text, filter_wiki_subtitles=True)
            links = set()
            for link in article['interlinks'].keys():
                processed_link = TextProcessingUtils.clean_text(text=link, use_lemmas=True, remove_stop_words=True,
                                                                lowercase=True)
                links.add(processed_link)
            writer.add_document(title=title.encode().decode('utf-8'), content=text, links=list(links))

            if counts % 50000 == 0:
                print("Added " + str(counts) + " documents.")

            if counts % 500000 == 0:
                writer.commit(merge=False)
                writer = ix.writer(limitmb=4096, procs=12, multisegment=True)
                print("Committing after " + str(counts) + " documents.")

            counts += 1
        try:
            print("Final commit: Added " + str(counts) + " documents.")
            writer.commit(merge=False)
        except Exception as e:
            print(e)

    def write_entities(self, output_target_file):
        with open(output_target_file, 'w') as f:
            f.write('\n'.join(list(self.entities)))

    def get_entities(self):
        return self.entities

    def load_entities(self, input_source_file):
        with open(input_source_file, 'rt') as f:
            self.entities = set(f.read().split('\n'))
        return self.entities
