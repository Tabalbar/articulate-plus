from datetime import datetime, timedelta

import numpy as np

from .extractor import Extractor
from .crawling_utils import  CrawlingUtils
from ..text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils


class CWBChicagoExtractor(Extractor):
    def __init__(self, output_target_file):
        super().__init__(None, output_target_file, 'http://www.cwbchicago.com/')

    def extract(self):
        d0 = datetime(2013, 5, 1)
        d1 = datetime(2018, 12, 13)
        dt = timedelta(days=1)

        dates = np.arange(d0, d1, dt).astype(datetime)
        for date in dates:
            archive_date = date.strftime('%Y_%m_%d')

            text = CrawlingUtils.get_text_from_url(self.base_url + archive_date + '_archive.html')

            paragraphs = []
            for paragraph in text.split('\\n'):
                processed_paragraph = TextProcessingUtils.clean_text(text=paragraph)
                if len(processed_paragraph) > 0:
                    paragraphs.append(processed_paragraph)

            if not CWBChicagoExtractor.is_valid_paragraphs(paragraphs):
                continue

            processed_paragraphs = CWBChicagoExtractor.clean_paragraphs(paragraphs)
            with open(self.output_target_file, 'a+') as f:
                f.write(processed_paragraphs)
                f.write('\n')

    @staticmethod
    def is_valid_paragraphs(paragraphs):
        return paragraphs[7] != 'home'

    @staticmethod
    def clean_paragraphs(paragraphs):
        start = 10
        end = -53
        processed_paragraphs = [paragraph for paragraph in paragraphs[start:end] \
                                if paragraph[0].isalnum() and paragraph.strip().lower() not in \
                                ['posted by', 'crime in boystown', 'at',
                                 'email to twittershare to facebookshare to pinterest',
                                 'email thisblogthis share to twittershare to facebookshare to pinterest',
                                 'am', 'pm', 'newer posts', 'image google', 'image google source', 'source google',
                                 'image source google', 'image google 1', 'image source google inc',
                                 'image source: google',
                                 'email facebook twitter youtube',
                                 'email thisblogthis! share to twittershare to facebookshare to pinterest',
                                 'follow us on twitter', 'follow us on facebook', 'twitter us', 'facebook us']]
        processed_paragraphs = ' '.join(processed_paragraphs)
        processed_paragraphs = processed_paragraphs.replace('image source google inc', '')
        processed_paragraphs = processed_paragraphs.replace('image source: google', '')
        processed_paragraphs = processed_paragraphs.replace('image google', '')
        processed_paragraphs = processed_paragraphs.replace('image google 1', '')

        return processed_paragraphs
