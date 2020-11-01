#!/usr/bin/env python3

# TODO: skip already downloaded files
# TODO: iterate backward to prevent changes to index displacing page.
from typing import List
from KonachanScraper import KonachanScraper
import requests_cache
import logconfig

import sys


def main():
    search_terms: List[str] = []
    last = None
    for arg in sys.argv[1:]:
        if last in ['--tag', '-t']:
            search_terms.append(arg)
        last = arg

    if not search_terms:
        print('No search terms specified! Use -t [tag] to specify.')
        exit(1)

    logconfig.applyLogDefaults()
    requests_cache.install_cache("scraper_main", backend="sqlite", expire_after=600)
    scraper = KonachanScraper()
    scraper.scrape(search_terms)


if __name__ == '__main__':
    main()
