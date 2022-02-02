import time
import urllib.parse
import urllib.request

import html2text
from bs4 import BeautifulSoup


class CrawlingUtils:
    @staticmethod
    def get_response_from_url(url):
        TOTAL_RETRIES = 3
        WAIT_DURATION = 30

        req = urllib.request.Request(url)
        for retries_cnt in range(TOTAL_RETRIES):
            try:
                req = urllib.request.Request(url)
                resp = urllib.request.urlopen(url)
                html = resp.read()
                return html
            except Exception as e:
                print("URLLIB Error. Let us retry in 30 seconds", e, url)
                time.sleep(WAIT_DURATION)
        return None

    @staticmethod
    def crawl_links_for_url(url):
        html = CrawlingUtils.get_response_from_url(url)
        if html is None:
            return None

        soup = BeautifulSoup(html)
        link_tags = soup.find_all('a')

        links = set()
        for link_tag in link_tags:
            tag = link_tag.get('href', None)

            if tag is None:
                continue
            if ':' in tag:
                continue

            if tag.startswith('/wiki/'):
                link = tag.replace('/wiki/', '')

                if link == 'Main_Page':
                    continue

                if link == 'Chicago':
                    continue

                links.add(link)
        return links

    @staticmethod
    def get_text_from_url(url, ignore_links=True, ignore_anchors=True, ignore_images=True, ignore_emphasis=True):
        print("Processing url " + url)

        html = CrawlingUtils.get_response_from_url(url)
        if html == None:
            return None
        html = str(html)
        handler = html2text.HTML2Text()
        handler.ignore_links = ignore_links
        handler.ignore_anchors = ignore_anchors
        handler.ignore_images = ignore_images
        handler.ignore_emphasis = ignore_emphasis

        return handler.handle(html)

    @staticmethod
    def get_text_from_html(html):
        soup = BeautifulSoup(html)
        text = soup.get_text()

        return text
