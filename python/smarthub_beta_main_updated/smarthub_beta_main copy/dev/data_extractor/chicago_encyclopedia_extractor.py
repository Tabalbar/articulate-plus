import re

from .crawling_utils import CrawlingUtils
from .extractor import Extractor
from ..text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils


class ChicagoEncyclopediaExtractor(Extractor):
    def __init__(self, output_target_file):
        super().__init__(None, output_target_file, 'http://www.encyclopedia.chicagohistory.org')

    def extract_entities_and_links(self):
        entities_and_links = []
        for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                       'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            text = CrawlingUtils.get_text_from_url(self.base_url + '/browse/entry' + letter + '.html',
                                                   ignore_links=False).split('\\r\\n')
            for entry in text:
                if '(' in entry:
                    entity_name = re.search('\\[(.*?)\\]', entry)
                    entity_link = re.search('\\((/.*?)\\)', entry)

                    entity_and_link = [None, None]

                    if entity_name is None:
                        continue

                    if entity_name is not None and entity_name.group()[1:-1]:
                        entity_and_link[0] = entity_name.group()[1:-1]
                        entity_and_link[0] = ChicagoEncyclopediaExtractor \
                            .clean_entity_name(entity_and_link[0])

                    if entity_link is not None:
                        entity_and_link[1] = entity_link.group()[1:-1]

                    if ChicagoEncyclopediaExtractor.is_valid_entity_name(
                            entity_and_link[0]):
                        entities_and_links.append(entity_and_link)

        return entities_and_links

    def extract_paragraphs_text_from_link(self, entity_link):
        text = TextProcessingUtils.clean_text(text=CrawlingUtils.get_text_from_url(self.base_url + entity_link))
        paragraphs = text.split('\n')[:-4]

        return paragraphs

    @staticmethod
    def is_paragraph_valid(paragraph):
        if 'index special features' in paragraph:
            return False

        if 'all rights reserved' in paragraph:
            return False

        if 'portions are copyrighted' in paragraph:
            return False

        if paragraph.strip() == '':
            return False

        return True

    @staticmethod
    def is_valid_entity_name(entity_name):
        return entity_name != 'Full Index' and entity_name != 'Maps' and \
               entity_name != 'Historical Sources' and entity_name != 'Special Features'

    def extract(self):
        entities_and_links = self.extract_entities_and_links()
        self.entities = [entity for entity, entity_link in entities_and_links if entity is not None]
        self.entities = sorted(list(set(self.entities)))

        for entity, entity_link in entities_and_links:
            if entity_link is None:
                continue

            paragraphs = self.extract_paragraphs_text_from_link(entity_link)

            for paragraph_index in range(len(paragraphs)):
                if paragraph_index == len(paragraphs) - 2:
                    break

                paragraph = paragraphs[paragraph_index]

                if not ChicagoEncyclopediaExtractor.is_paragraph_valid(paragraph):
                    continue

                paragraph = TextProcessingUtils.remove_repeated_words_from_beginning(paragraph)

                with open(self.output_target_file, 'a+') as f:
                    f.write(paragraph)
                    f.write('\n')

            with open(self.output_target_file, 'a+') as f:
                f.write('\n')

    @staticmethod
    def clean_entity_name(entity_name):
        entity_name = entity_name.replace(' Co.', '')
        entity_name = entity_name.replace(' Corp.', '')
        entity_name = entity_name.replace(' Inc.', '')
        entity_name = entity_name.replace('\s', '')
        entity_name = entity_name.replace("\\'n\\' ", "")
        entity_name = entity_name.replace("\\'s", "")
        entity_name = entity_name.replace("\\'", "")

        tokens = entity_name.split(':')
        entity_name = tokens[0]

        entity_name = entity_name.replace('"', '')

        if '&' not in entity_name:
            return entity_name

        tokens = entity_name.split()
        if tokens[len(tokens) - 1] != '&':
            entity_name = entity_name.replace('&', 'and')
            return entity_name

        first = tokens[1]
        last = tokens[0]

        if last[-1] == ',':
            last = last[:-1]
        entity_name = first + ' and ' + last

        return entity_name

    def write_entities(self, output_target_file):
        with open(output_target_file, 'w') as f:
            f.write('\n'.join(self.entities))

    def get_entities(self):
        if len(self.entities) == 0:
            entities_and_links = self.extract_entities_and_links()
            self.entities = [entity for entity, entity_link in entities_and_links \
                             if entity is not None]
        return sorted(list(set(self.entities)))

    def load_entities(self, input_source_file):
        with open(input_source_file, 'rt') as f:
            self.entities = f.read().split('\n')
        return self.entities
