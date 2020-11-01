#!/usr/bin/env python3

from pathlib import Path
from typing import List
from KonachanScraper import KonachanScraper
import requests_cache
import logconfig
import sys
import configparser


# TODO: switch to Confuse module, or similar arg/config parsing abstraction library.
# TODO: refactor to replace linear "look up as needed" model with an indexing system.
# TODO: scrap 'search page' parsing routine... slows us down significantly.
#   * posts seem to be numbered from like 1 to number like 20000 or somesuch.
#       could make easy to simply iterate over `https://konachan.com/post/[number]` and ignore the search interface entirely.
#       Just blindly iterate over every post and grab the tags & full size URL. Then can later download anything filtered from index.
#       Then update the index iff blind downloading fails later on (because fullsize image URLs seem to be built from tags).
#       Would also have the advantage of bypassing the site's broken search features. (e.g., not filtering tags on later pages)
# Once indexing is added:
# TODO: add feature for recording downloaded file checksums, to indexing.
# TODO: update indexes for all local files. Files will be reindexed automatically if change is detected since the program was last run?
#       (requires checking timestamps on everything on each run... :/)
# TODO: Far future: maybe add automatic file sorting?
# Some unknowns:
#   * do file IDs change if file is deleted? 

# TODO: switch to parallel operation model.
#       * Have maybe 5 threads each iterating over assigned posts. Might want to use asyncio, or could do manually with multithread lib.
def main():
    config = configparser.ConfigParser()
    config['DEFAULT']['blacklist'] = 'shoda,loli,male, flat_chest'

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
