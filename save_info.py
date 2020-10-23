import json
import os


class Reader():
    def __init__(self, obj, filen):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.obj = obj
        self.filen = filen

    def read_json(self, last_id=0):
        self.obj = {}
        self.obj['last_id'] = last_id
        source_path = os.path.join(self.dir_path, self.filen)
        if os.path.exists(source_path):
            print(f'--- Restoring from file: {source_path}')
            with open(source_path, 'r') as json_file:
                input_dict = json.load(json_file)
            for game in input_dict['games']:
                id = game['id']
                self.obj[id] = game
        else:
            print(f'!!! No file found at: {source_path}')
        return self.obj


class Writer():
    def __init__(self, obj, filen):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.obj = obj
        self.filen = filen

    def set_obj(self, obj):
        self.obj = obj

    def update_obj(self, db):
        output = {}
        output['games'] = []
        for key in db.keys():
            if key != 'last_id':
                try:
                    output['games'].append(db[key])
                except KeyError:
                    print('!!! Local Shelve Database may be corrupted!')
        self.obj = output

    def dump_to_file(self, verbose=False):
        if verbose:
            print('--- Dumping to file: {}'.format(self.filen))
        with open(os.path.join(self.dir_path, self.filen), 'w') as json_file:
            json.dump(self.obj, json_file, indent=2)
