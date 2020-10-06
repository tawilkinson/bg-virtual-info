import requests
from urllib.parse import urlunsplit, urlencode
from bs4 import BeautifulSoup
from save_info import Writer


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
        try:
            desc = self.soup.find('meta',  property='og:description')[
                'content']
        except:
            desc = ''
        return desc

    def get_image(self):
        try:
            image = self.soup.find('meta',  property='og:image')['content']
        except:
            image = ''
        return image

    def get_site(self, name, app=False, bga=False, boite=False, tabletopia=False, tts=False, yucata=False):
        site = ''
        if app:
            # TODO: work out best way to try and find app using Google search
            pass
        if bga:
            html = requests.get(
                'https://boardgamearena.com/gamelist?section=all')
            soup = BeautifulSoup(html.text, 'html.parser')
            all_games = soup.find_all('div', class_='gamelist_item')
            for game in all_games:
                if name in game.find_all('div')[1].text:
                    site = '[{}]('.format(name)
                    site += 'https://boardgamearena.com'
                    site += game.find(href=True)['href']
                    site += ')'
                    return site
        if boite:
            html = requests.get('http://www.boiteajeux.net/index.php?p=regles')
            soup = BeautifulSoup(html.text, 'html.parser')
            all_games = soup.find_all('div', class_='jeuxRegles')
            for game in all_games:
                if name.lower() in game.text.lower():
                    site += '[{}]('.format(name)
                    site += 'http://www.boiteajeux.net/index.php?p=regles'
                    site += ')'

            if site == '':
                return False
            else:
                return site
        if tabletopia:
            # TODO: Need JS scraping
            pass
        if tts:
            html = requests.get(
                'https://store.steampowered.com/dlc/286160/Tabletop_Simulator/#browse')
            soup = BeautifulSoup(html.text, 'html.parser')
            all_games = soup.find_all('a', class_='recommendation_link')
            for game in all_games:
                if name.lower() in game.text.lower():
                    site += '[TTS DLC - {}]('.format(name)
                    site += game['href']
                    site += ')\n'

            if site == '':
                return False
            else:
                return site
        if yucata:
            html = requests.get('https://www.yucata.de/en')
            soup = BeautifulSoup(html.text, 'html.parser')
            all_games = soup.find_all('a')
            for game in all_games:
                if name in game.text:
                    site += '[{}]('.format(game.text)
                    site += 'https://www.yucata.de'
                    site += game['href']
                    site += ')\n'

            if site == '':
                return False
            else:
                return site
        return False

    def get_game(self):
        self.html = requests.get(self.current_url)

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
            # Only save games that are available to play virtually somewhere
            if tabletopia or tts or bga or yucata or boite or app:
                save = True
            else:
                save = False
            game = self.game_setter(
                name, description, bgg, image, tabletopia, tts, bga, yucata, boite, app)
        else:
            game = self.game_setter()
            success = False

        return game, success, save


def main():
    bgg_scraper = scraper('boardgamegeek.com')
    scrape(bgg_scraper, 190000, True)


def scrape(scraper, largest_id=100, verbose=False):
    print('Base url to search: {}'.format(scraper.current_url))
    output = {}
    output['games'] = []
    for num in range(1, largest_id+1):
        scraper.increment_url(num=num)
        if verbose:
            print('Now searching: {}'.format(scraper.current_url))
        game, success, save = scraper.get_game()
        if success and save:
            output['games'].append(game)
            print('Adding {}, {} games in database'.format(
                game['name'], len(output['games'])))
        else:
            # Could log issues here
            if verbose:
                print('Skipping {}'.format(game['name']))

    write = Writer(output, 'games.json')
    write.dump_to_file()


if __name__ == '__main__':
    # execute only if run as a script
    main()
