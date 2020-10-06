import requests
import argparse
import shelve
from urllib.parse import urlunsplit, urlencode
from urllib3 import exceptions
from bs4 import BeautifulSoup
import save_info


class Scraper():
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
        print('--- Caching Board Game Arena')
        self.setup_bga()
        print('+++ {} games added'.format(len(self.bga_dict)))
        print('--- Caching Boîte à Jeux')
        self.setup_boite()
        print('+++ {} games added'.format(len(self.boite_dict)))
        print('--- Caching Tabletop Simulator')
        self.setup_tts()
        print('+++ {} games added'.format(len(self.tts_dict)))
        print('--- Caching Yucata')
        self.setup_yucata()
        print('+++ {} games added'.format(len(self.yucata_dict)))

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
            print('!!! Can\'t get Boite a Jeux data')
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

    def setup_tts(self):
        try:
            html = requests.get(
                'https://store.steampowered.com/dlc/286160/Tabletop_Simulator')
        except:
            print('!!! Can\'t get Tabletop Simulator data')
            exit()
        soup = BeautifulSoup(html.text, 'html.parser')
        all_games = soup.find_all('a', class_='recommendation_link')
        self.tts_dict = {}
        for game in all_games:
            name = game.find('span', class_='color_created').text
            site = '[{}]('.format(name)
            site += game['href']
            site += ')'
            self.tts_dict[name] = site

    def setup_yucata(self):
        try:
            html = requests.get('https://www.yucata.de/en')
        except:
            print('!!! Can\'t get Yucata data')
            exit()
        soup = BeautifulSoup(html.text, 'html.parser')
        all_games = soup.find_all('a')
        self.yucata_dict = {}
        for game in all_games:
            name = game.text
            site = '[{}]('.format(game.text)
            site += 'https://www.yucata.de'
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
        game_dict = {}
        game_dict['id'] = id
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
            # TODO: Need JS scraping
            pass
        if tts:
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

    bgg_scraper = Scraper('boardgamegeek.com')
    scrape(bgg_scraper, args.start, args.end, args.verbose, args.restart)


def scrape(scraper, start=1, end=100, verbose=False, resume=True):
    print('--- Base url to search: {}'.format(scraper.current_url))

    with shelve.open('games') as db:
        try:
            if db['last_id'] > 0 and resume:
                print('--- Resuming from id: {}'.format(db['last_id']))
                start = db['last_id'] + 1
        except:
            print('!!! No stored data, start from start')
            db['last_id'] = 0

        for num in range(start, end+1):
            db['last_id'] = num
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
                db[str(num)] = game
                print('+++ Adding id:{} - {}, {} games in database'.format(
                    num, game['name'], len(db)))
            else:
                # Could log issues here
                if verbose:
                    print('!!! Skipping {}'.format(game['name']))

        output = {}
        output['games'] = []
        for key in db.keys():
            if key != 'last_id':
                output['games'].append(db[key])
    print(
        '--- Finished: {} games in database'.format(len(output['games'])))
    write = save_info.Writer(output, 'games.json')
    write.dump_to_file()


if __name__ == '__main__':
    # execute only if run as a script
    main()
