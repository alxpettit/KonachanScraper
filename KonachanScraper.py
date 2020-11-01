from pathlib import Path
from typing import List, Pattern
import urllib.parse

import bs4
import logging
import re
import requests
import utils
import html

# TODO: make 'lewd' dir be created if it doesn't exist!!

re_url_identifier = re.compile("^https?://")
re_original_file_generic = re.compile("original-file")


class KonachanScraper:
    """ Scraper for Konachan site made for a dear friend of mine.
        The layout is very simple. We take a given search term and iterate over every search result page.
        Then we iterate over those results and load each of their pages to get the fullsize image link.
    """
    logger: logging.Logger = None
    _soup: bs4.Tag = None
    _url: str = None
    target_dir: Path = Path('lewd')
    blacklisted_tags: List[str] = []

    def __init__(self):
        self.logger = logging.getLogger("KonachanScraper")
        try:
            self.target_dir.mkdir()
        except FileExistsError:
            pass
        self.logger.info("Initialized.")

    def scrape(self, search_terms: List[str], base_url: str = "https://konachan.com/post"):
        quoted_search_terms: List[str] = [urllib.parse.quote(string) for string in search_terms]
        quote_string: str = '+'.join(quoted_search_terms)
        i: int = 1
        while True:
            if i > 1:
                # Fun fact: if you have tags first, Konachan will assume the '?page' arg is a tag. :S
                url = f'{base_url}?page={i}?tags={quote_string}'
            else:
                url = f'{base_url}?tags={quote_string}'
            self.logger.info(f'Search page URL: {url}')
            self.logger.info(f"Now on page {i}")
            request_search_page: requests.Response = requests.get(url)
            self._soup = bs4.BeautifulSoup(request_search_page.text, 'html.parser')
            if not self.iterateOverSearchResults():
                self.logger.info('This appears to be the last page. Halting!')
                break
            i += 1

    @staticmethod
    def tagFindLink(tag: bs4.Tag, attrs: dict, recursive: bool = True):
        attrs.update({'href': re_url_identifier})
        return tag.find('a', attrs=attrs, recursive=recursive)

    def getBestImageFromPostPage(self, url_post_page: str) -> str:
        """ Get download link for 'full-size image' from post page. """
        self.logger.info(f'Processing post link: {url_post_page}')
        url_post_page_response: requests.Response = requests.get(url_post_page)
        url_post_page_soup = bs4.BeautifulSoup(url_post_page_response.text, 'html.parser')
        link_tag = self.tagFindLink(url_post_page_soup, {'class': 'original-file'})
        if not link_tag:
            link_tag = self.tagFindLink(url_post_page_soup, {'class': re_original_file_generic})
        if not link_tag:
            self.logger.error(f'Couldn\'t parse download link from post page: {url_post_page}')
            return ""
        return str(link_tag.get('href', re_url_identifier))

    def containsBlacklisted(self, string: str):
        for tag in self.blacklisted_tags:
            if tag in string.split():
                return True
        return False

    def handleImagePost(self, image_post: bs4.Tag) -> bool:
        url_without_tag: str = image_post.text[len('#pl'):]
        image_download_url: str = self.getBestImageFromPostPage(url_without_tag)

        fname: str = utils.getFileNameFromURL(image_download_url)
        fname = fname[len('Konachan.com - '):]
        file_path: Path = self.target_dir / fname
        if self.containsBlacklisted(fname):
            self.logger.warning(f'Skipping: "{fname}" due to blacklist.')
            return False
        if image_download_url == "":
            self.logger.warning(f'Skipping download for page: "{url_without_tag}"')
        with utils.DelayedKeyboardInterrupt():
            self.logger.info(f'Downloading file: "{fname}"')
            if not file_path.exists():
                utils.dl_file(image_download_url, file_path)
            else:
                self.logger.warning(f'Skipping existing file: "{file_path}"')
        return True

    def iterateOverSearchResults(self) -> bool:
        image_posts: List[bs4.Tag] = self._soup.find_all('span', attrs={'class': 'plid'}, recursive=True)
        if not image_posts:
            return False
        for image_post in image_posts:
            self.handleImagePost(image_post)
        return True
