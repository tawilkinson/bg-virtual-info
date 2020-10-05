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

    def game_setter(self, name='', description='', bgg='', image='',
                    tabletopia=False, tts=False, bga=False, yucata=False,
                    boite=False, app=False):
        game_dict = {}
        game_dict['name'] = name
        game_dict['description'] = description
        game_dict['bgg'] = bgg
        game_dict['image'] = image
        game_dict['tabletopia'] = tabletopia
        game_dict['tts'] = tts
        game_dict['bga'] = bga
        game_dict['yucata'] = yucata
        game_dict['boite'] = boite
        game_dict['app'] = app
        return game_dict

    def get_bgg(self):
        bgg = self.html.url
        return bgg

    def get_name(self):
        success = True
        try:
            name = self.soup.find('meta',  property='og:title')['content']
            if name == '':
                success = False
        except:
            name = ''
            success = False
        return name, success

    def get_desc(self):
        desc = self.soup.find('meta',  property='og:description')['content']
        return desc

    def get_image(self):
        image = self.soup.find('meta',  property='og:image')['content']
        return image

    def get_site(self, name, app=False, bga=False, boite=False, tabletopia=False, tts=False, yucata=False):
        site = ''
        if app:
            site = '[{} App]('.format(name)
            site += 'url'
            site += ')'
            return site
        if bga:
            html = requests.get(
                'https://boardgamearena.com/gamelist?section=all')
            soup = BeautifulSoup(html.text, 'html.parser')
            all_games = soup.find_all('div', class_='gamelist_item')
            for game in all_games:
                if name in game.find_all('div')[1].text:
                    site = '[{} on Board Game Arena]('.format(name)
                    site += 'https://boardgamearena.com'
                    site += game.find(href=True)['href']
                    site += ')'
                    print(site)
                    return site
        if boite:
            site = '[{} on Boîte a Jeux]('.format(name)
            site += 'url'
            site += ')'
            return site
        if tabletopia:
            site = '[{} on Tabletopia]('.format(name)
            site += 'url'
            site += ')'
            return site
        if tts:
            site = '[{} on TableTop Simulator]('.format(name)
            site += 'url'
            site += ')'
            return site
        if yucata:
            site = '[{} on Yucata]('.format(name)
            site += 'url'
            site += ')'
            return site
        return False

    def get_game(self):
        self.html = requests.get(self.current_url)

        # print(self.html.text)
        if self.html.status_code == 200:
            self.soup = BeautifulSoup(self.html.text, 'html.parser')
            bgg = self.get_bgg()
            name, success = self.get_name()
            description = self.get_desc()
            image = self.get_image()
            tabletopia = self.get_site(name, tabletopia=True)
            tts = self.get_site(name, tts=True)
            bga = self.get_site(name, bga=True)
            yucata = self.get_site(name, yucata=True)
            boite = self.get_site(name, boite=True)
            app = self.get_site(name, app=True)
            game = self.game_setter(
                name, description, bgg, image, tabletopia, tts, bga, yucata, boite, app)
        else:
            game = self.game_setter()
            success = False
        print(game)

        return game, success


def main():
    bgg_scraper = scraper('boardgamegeek.com')
    scrape(bgg_scraper, 6, True)


def scrape(scraper, largest_id=100, verbose=False):
    print('Base url to search: {}'.format(scraper.current_url))
    output = {}
    output['games'] = []
    # for num in range(1, largest_id+1):
    for num in range(820, 823):
        scraper.increment_url(num=num)
        if verbose:
            print('Now searching: {}'.format(scraper.current_url))
        game, success = scraper.get_game()
        if success:
            output['games'].append(game)
        else:
            # Could log issues here
            if verbose:

                print('Skipping {}'.format(scraper.current_url))


if __name__ == '__main__':
    # execute only if run as a script
    main()
