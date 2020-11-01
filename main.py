#!/usr/bin/env python3

from pathlib import Path
from typing import List
from KonachanScraper import KonachanScraper
import requests_cache
import logconfig
import sys
import configparser


def main():
    config = configparser.ConfigParser()
    config['DEFAULT']['blacklist'] = 'shoda,loli,male'

    config_path = Path('config.ini')
    if config_path.exists():
        config.read(open(config_path))

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
    scraper.blacklisted_tags = config['DEFAULT']['blacklist'].split(',')
    scraper.scrape(search_terms)


if __name__ == '__main__':
    main()
