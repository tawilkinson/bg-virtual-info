import requests
from urllib.parse import urlunsplit, urlencode
from bs4 import BeautifulSoup


class scraper():
    def __init__(self, base_url, https=True):
        self.base_url = base_url
        self.current_url = base_url
        self.id = 0
        if https:
            self.scheme = 'https'
        else:
            self.scheme = 'http'
        self.base_path = ''
        if 'boardgamegeek' in base_url:
            self.setup_bgg()
        self.set_url()

    def setup_bgg(self):
        self.base_path = '/boardgame/'

    def set_url(self):
        if self.id:
            path = f'{self.base_path}{self.id}'
        else:
            path = f'{self.base_path}'
        self.current_url = urlunsplit(
            (self.scheme, self.base_url, path, '', ''))

    def increment_url(self, num=0):
        if num:
            self.id = num
        else:
            self.id += 1
        self.set_url()


def main():
    bgg_scraper = scraper('boardgamegeek.com')
    scrape(bgg_scraper, 60000)


def scrape(scraper, largest_id=100):
    print('Base url to search: {}'.format(scraper.current_url))
    for num in range(1, largest_id+1):
        scraper.increment_url(num=num)
        print('Now searching: {}'.format(scraper.current_url))


if __name__ == '__main__':
    # execute only if run as a script
    main()
