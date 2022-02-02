from .crawling_utils import CrawlingUtils
from .extractor import Extractor
from ..text_tokenizer_pipeline.text_processing_utils import TextProcessingUtils


class ChicagoSunTimesNeighborhoodsExtractor(Extractor):
    def __init__(self, output_target_file):
        super().__init__(None, output_target_file, 'https://chicago.suntimes.com/')

    def extract(self):
        urls = [self.base_url + 'instagram/the-grid-exploring-the-logan-square-neighborhood-things-to-do/',
                self.base_url + 'news/exploring-andersonville-neighborhood-things-to-do/',
                self.base_url + 'news/pilsen-neighborhood-things-to-do-dining-shopping-events-the-grid/',
                self.base_url + 'entertainment/the-grid-exploring-hyde-park-neighborhood-things-to-do/',
                self.base_url + 'entertainment/the-grid-exploring-ravenswood-neighborhood-things-to-do/',
                self.base_url + 'entertainment/the-grid-exploring-printers-row-neighborhood-things-to-do/',
                self.base_url + 'news/grid-exploring-roscoe-village-chicago-neighborhood-things-to-do-eat-drink-shop-restaurants-riverview-park/',
                self.base_url + 'entertainment/the-grid-bronzeville-neighborhood-things-to-do-chicago-weekend-restaurants-history-african-american-culture-great-migration-tour/',
                self.base_url + 'entertainment/the-grid-rogers-park-neighborhood-visit-chicago-things-to-do-restaurants-events-weekend-visit-chicago-apartments-beach-murals-public-art/',
                self.base_url + 'entertainment/the-grid-chinatown-neighborhood-things-to-do-restaurants-festivals-events-shopping-chinese-food-chicago/',
                self.base_url + 'entertainment/chicago-exploring-south-shore-neighborhood-things-to-do-food-history-the-grid/',
                self.base_url + 'entertainment/boystown-lgbtq-neighborhood-things-to-do-food-history-the-grid/',
                self.base_url + 'entertainment/norwood-park-neighborhood-things-to-do-best-places-to-eat-the-grid/',
                self.base_url + 'entertainment/old-town-neighborhood-things-to-do-second-city/',
                self.base_url + 'instagram/ukrainian-village-neighborhood-eat-shop-churches-things-to-do/',
                self.base_url + 'instagram/bridgeport-chicago-neighborhood-exploring-things-to-do-the-grid/',
                self.base_url + 'instagram/edison-park-dining-best-restaurants-things-to-do-parks-events-the-grid/',
                self.base_url + 'entertainment/pullman-neighborhood-chicago-history-walking-tours-industry-things-to-do/',
                self.base_url + 'entertainment/little-italy-neighborhood-best-restaurants-things-to-do/',
                self.base_url + 'entertainment/exploring-greektown-food-things-to-do-neighborhood-history-the-grid/',
                self.base_url + 'entertainment/avondale-neighborhood-things-to-do/',
                self.base_url + 'instagram/uptown-neighborhood-things-to-do-restaurants/',
                self.base_url + 'entertainment/auburn-gresham-neighborhood-bungalow-belt-soul-food-saint-sabina/']

        with open(self.output_target_file, 'w+') as f:
            f.write(
                '\n'.join([TextProcessingUtils.clean_text(text=CrawlingUtils.get_text_from_url(url)) for url in urls]))
