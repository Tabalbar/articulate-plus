import re

from .crawling_utils import CrawlingUtils
from .extractor import Extractor
from ..text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils


class CJPNewsArticlesExtractor(Extractor):
    def __init__(self, input_source_file, output_target_file):
        super().__init__(input_source_file, output_target_file, None)

    def extract(self):
        print("Load articles from file " + self.input_source_file)
        with open(self.input_source_file, 'rt') as f:
            html = f.read()

        page_boundary = '<div class=""trb_ar_page"" data-content-page=""[\d]+"" data-role=""pagination_page"">'
        html_pages = re.split(page_boundary, html)

        total_html_pages = len(html_pages)
        html_page_cnt = 0
        for html_page in html_pages:
            processed_text = TextProcessingUtils.clean_text(text=CrawlingUtils.get_text_from_html(html_page))
            if processed_text == None:
                continue

            print("Writing html page " + str(html_page_cnt) + " out of " + str(
                total_html_pages) + " to " + self.output_target_file)
            with open(self.output_target_file, 'a+') as f:
                f.write(processed_text)
                f.write('\n')

            html_page_cnt += 1
