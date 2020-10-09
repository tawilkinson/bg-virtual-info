import requests
import argparse
import shelve
import time
import lxml
from urllib.parse import urlunsplit, urlencode
from urllib3 import exceptions
from bs4 import BeautifulSoup
import save_info


class Webpage(BeautifulSoup):
    def __init__(self, url):
        self.response = requests.get(url)
        self.page_response = self.response
        self.page_html = BeautifulSoup(self.response.text, 'lxml')


class Game():
    def __init__(self, id=0, name='', description='', bgg='', image='',
                 tabletopia=False, tts=False, bga=False, yucata=False,
                 boite=False, app=False):
        self.id = id
        self.name = name
        self.description = description
        self.bgg = bgg
        self.image = image
        self.tabletopia = tabletopia
        self.tts = tts
        self.bga = bga
        self.yucata = yucata
        self.boite = boite
        self.app = app

    def get_game_dict(self):
        game_dict = {}
        game_dict['id'] = self.id
        game_dict['name'] = self.name
        game_dict['description'] = self.description
        game_dict['bgg'] = self.bgg
        game_dict['image'] = self.image
        game_dict['tabletopia'] = self.tabletopia
        game_dict['tts'] = self.tts
        game_dict['bga'] = self.bga
        game_dict['yucata'] = self.yucata
        game_dict['boite'] = self.boite
        game_dict['app'] = self.app
        return game_dict

    def print_game(self):
        print(f'Game: {self.name} - BGG ID: {self.id}')
        print(f'Description: \n"{self.description}"')
        if self.bgg:
            print(f'On Board Game Geek: {self.bgg}')
            print(f'With image: {self.image}')
        if self.app:
            print(f'Has an app: {self.app}')
        if self.bga:
            print(f'On Board Game Arena: {self.bga}')
        if self.boite:
            print(f'On Boîte à Jeux: {self.boite}')
        if self.tabletopia:
            print(f'On Tabletopia: {self.tabletopia}')
        if self.tts:
            print(f'On Tabletop Simulator: {self.tts}')
        if self.yucata:
            print(f'On Yucata: {self.yucata}')


class Scraper():
    def __init__(self, https=True):
        self.base_url = 'boardgamegeek.com'
        self.current_url = 'boardgamegeek.com'
        self.id = 0
        if https:
            self.scheme = 'https'
        else:
            self.scheme = 'http'
        self.base_path = ''
        self.setup_bgg()
        self.bga_search_url = f'https://boardgamearena.com/gamepanel?game='
        self.bgg_search_url = f'http://www.boardgamegeek.com/xmlapi2/search?query='
        self.boite_search_url = 'http://www.boiteajeux.net/index.php?p=regles'
        self.tabletopia_search_url = f'https://tabletopia.com/playground/playgroundsearch/search?timestamp='
        self.tts_dlc_url = 'https://store.steampowered.com/search/?term=tabletop+simulator&category1=21'
        self.tts_search_url = f'https://steamcommunity.com/workshop/browse/?appid=286160&searchtext='
        self.tts_qualifiers = f'&browsesort=textsearch&section=readytouseitems&requiredtags%5B0%5D=Game&actualsort=textsearch&p=1'
        self.yucata_search_url = 'https://www.yucata.de/en/'
        self.set_url()
        print('--- Caching Board Game Arena')
        self.setup_bga()
        print('+++ {} games added'.format(len(self.bga_dict)))
        print('--- Caching Boîte à Jeux')
        self.setup_boite()
        print('+++ {} games added'.format(len(self.boite_dict)))
        print('--- Initialising Tabletopia Cache')
        self.setup_tabletopia()
        print('--- Caching Tabletop Simulator')
        self.setup_tts()
        print('+++ {} games added'.format(len(self.tts_dict)))
        print('--- Caching Yucata')
        self.setup_yucata()
        print('+++ {} games added'.format(len(self.yucata_dict)))

    def make_bga_url(self, name):
        return self.bga_search_url + '{name}'

    def make_bgg_search_url(self, name, exact=True):
        if exact:
            return self.bgg_search_url + f'{name}&exact=1&type=boardgame'
        else:
            return self.bgg_search_url + f'{name}&exact=0&type=boardgame'

    def make_tabletopia_search_url(self, name):
        return self.tabletopia_search_url + f'{int(time.time() * 1000)}&query={name}'

    def make_tts_search_url(self, name):
        return self.tts_search_url + f'{name}' + self.tts_qualifiers

    def setup_bga(self):
        try:
            html = requests.get(
                'https://boardgamearena.com/gamelist?section=all')
        except:
            print('!!! Can\'t get Board Game Arena data')
            exit()
        soup = BeautifulSoup(html.text, 'html.parser')
        all_games = soup.find_all('div', class_='gamelist_item')
        self.bga_dict = {}
        for game in all_games:
            name = game.find(
                'div', class_='gameitem_baseline gamename').text.lstrip().rstrip()
            site = '[{}]('.format(name)
            site += 'https://boardgamearena.com'
            site += game.find(href=True)['href']
            site += ')'
            self.bga_dict[name] = site

    def setup_boite(self):
        try:
            html = requests.get('http://www.boiteajeux.net/index.php?p=regles')
        except:
            print('!!! Can\'t get Boîte à Jeux data')
            exit()
        soup = BeautifulSoup(html.text, 'html.parser')
        self.boite_dict = {}
        all_games = soup.find_all('div', class_='jeuxRegles')
        for game in all_games:
            name = game.text.lower().lstrip().split('\n')[0]
            site = '[{}]('.format(name)
            site += 'http://www.boiteajeux.net/index.php?p=regles'
            site += ')'
            self.boite_dict[name] = site

    def setup_tabletopia(self):
        self.tabletopia_dict = {}

    def search_tabletopia(self, name):
        # Don't waste time on games already in dict
        for key in self.tabletopia_dict:
            if name == key:
                return
        tabletopia_directory_page = Webpage(
            self.make_tabletopia_search_url(name)).page_html
        search_results = tabletopia_directory_page.find_all(
            'a', class_='dropdown-menu__item dropdown-item-thumb')
        for result in search_results:
            game_name = result.text.strip()
            game_tabletopia_url = result['href']
            game_tabletopia_url = f'https://tabletopia.com{game_tabletopia_url}'
            formatted_link = f'[{game_name} on Tabletopia]({game_tabletopia_url})'
            if name == game_name:
                self.tabletopia_dict[game_name] = formatted_link
                print('+++ Caching {} to Tabletopia: {} games on Tabletopia'.format(game_name,
                                                                                    len(self.tabletopia_dict)))

    def setup_tts(self):
        tts_dlc = Webpage(self.tts_dlc_url)
        tts_dlc_html = tts_dlc.page_html
        self.tts_dict = {}
        if tts_dlc.response.status_code == 200:
            all_games = tts_dlc_html.find_all(
                'div', {'class': 'search_name'})

            for game in all_games:
                this_name = game.text.lstrip('\n').rstrip('\n ')
                name = this_name.replace('Tabletop Simulator - ', '')
                if 'Tabletop Simulator' in this_name:
                    url = game.parent.parent['href']
                    url = url.split('?snr=')[0]
                    site = f'[{this_name}]({url})'
                    self.tts_dict[name] = site
        else:
            print('!!! Can\'t get Tabletop Simulator data')

    def search_tts(self, name):
        # Don't lose the official DLC
        sites = []
        for key in self.tts_dict:
            name_check = 'Tabletop Simulator - ' + name
            if name_check == key:
                sites.append(self.tts_dict[key])
        tts_search = Webpage(self.make_tts_search_url(name)).page_html
        search_results = tts_search.find_all(
            'div', {'class': 'workshopItemTitle'})
        for result in search_results:
            game_name = result.text
            url = result.parent['href']
            if 'https://steamcommunity.com' in url:
                url = url.replace(
                    '/url?q=',
                    '').replace(
                    '%3F',
                    '?').replace(
                    '%3D',
                    '=').split('&')[0]
                if name in game_name:
                    sites.append(f'[{game_name}]({url})')
        if len(sites) and name:
            self.tts_dict[name] = '\n'.join(sites)
            print(
                '+++ Caching {} to Tabletop Simulator: {} games on TTS'.format(name, len(self.tts_dict)))

    def setup_yucata(self):
        try:
            html = requests.get(self.yucata_search_url)
        except:
            print('!!! Can\'t get Yucata data')
            exit()
        soup = BeautifulSoup(html.text, 'html.parser')
        all_games = soup.find_all('a')
        self.yucata_dict = {}
        for game in all_games:
            name = game.text
            if 'GameInfo' in game['href']:
                site = '[{}]('.format(game.text)
                site += self.yucata_search_url[:-4]
                site += game['href']
                site += ')'
                self.yucata_dict[name] = site

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

    def game_setter(self, id, name='', description='', bgg='', image='',
                    tabletopia=False, tts=False, bga=False, yucata=False,
                    boite=False, app=False):
        game = Game(id, name, description, bgg, image,
                    tabletopia, tts, bga, yucata, boite, app)
        return game.get_game_dict()

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
        games = []
        separator = '\n'
        if app:
            # TODO: work out best way to try and find app using Google search
            pass
        if bga:
            for key in self.bga_dict:
                if name == key:
                    games.append(self.bga_dict[key])
            site = separator.join(games)
        if boite:
            for key in self.boite_dict:
                if name.lower() == key:
                    games.append(self.boite_dict[key])
            site = separator.join(games)
        if tabletopia:
            self.search_tabletopia(name)
            for key in self.tabletopia_dict:
                if name in key:
                    games.append(self.tabletopia_dict[key])
            site = separator.join(games)
        if tts:
            self.search_tts(name)
            for key in self.tts_dict:
                if name == key:
                    games.append(self.tts_dict[key])
            site = separator.join(games)
        if yucata:
            for key in self.yucata_dict:
                if name == key:
                    games.append(self.yucata_dict[key])
            site = separator.join(games)
        if site:
            return site
        return False

    def get_game(self, id):
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
                id, name, description, bgg, image, tabletopia, tts, bga, yucata, boite, app)
        else:
            game = self.game_setter(id)
            success = False

        return game, success, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Verbose output',
                        action='store_true')
    parser.add_argument('-s', '--start', help='Starting page to scrape',
                        type=int, default=1)
    # approx 190,000 entries at time of writing script
    parser.add_argument('-e', '--end', help='End page to scrape',
                        type=int, default=190000)
    parser.add_argument('-r', '--restart', help='Ignore previously acquired data and overwrite',
                        action='store_false')
    args = parser.parse_args()

    print('--- Scraping BGG from {} to {}'.format(args.start, args.end))
    
    restart = True
    if not args.restart or args.start > 1:
        # This will clear local cache
        restart = False

    bgg_scraper = Scraper()
    scrape(bgg_scraper, args.start, args.end, args.verbose, restart)


def scrape(scraper, start=1, end=100, verbose=False, resume=True):
    print('--- Base url to search: {}'.format(scraper.current_url))

    write = save_info.Writer({}, 'games.json')

    with shelve.open('games') as db:
        try:
            if db['last_id'] > 0 and resume:
                print('--- Resuming from id: {}'.format(db['last_id']))
                start = db['last_id'] + 1
            else:
                print(
                    '!!! Wiping {} games from local cache [--restart]'.format(len(db)))
                db.clear()
        except:
            print('!!! No stored data, start from start')
            db['last_id'] = 0

        for num in range(start, end+1):

            scraper.increment_url(num=num)
            if verbose:
                print('--- Now searching: {}'.format(scraper.current_url))
            try:
                game, success, save = scraper.get_game(num)
            except ConnectionError:
                success = False
                print('!!! Connection Error')
            except exceptions.MaxRetryError:
                success = False
                print('!!! Max Retry Error')
                # Likely due to server rejecting too many connections
                break

            if success and save:
                db['last_id'] = num
                db[str(num)] = game
                print('+++ Adding id:{} - {}, {} games in database'.format(
                    num, game['name'], len(db)-1))
                # Dump results every 10 games
                if ((len(db)-1) % 10) == 0:
                    write.update_obj(db)
                    if verbose:
                        print(
                            '--- {} games, dumping to json'.format(len(write.obj['games'])))
                    write.dump_to_file(verbose)
            else:
                # Could log issues here
                if verbose:
                    print('!!! Skipping {}'.format(game['name']))
            db['last_id'] = num

        write.update_obj(db)
    print(
        '--- Finished: {} games in database'.format(len(write.obj['games'])))
    write.dump_to_file(True)


if __name__ == '__main__':
    # execute only if run as a script
    main()
