import json
import os


class Writer():
    def _init__(self, obj, filen):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.obj = obj
        self.filen = filen

    def dump_to_file(self):
        with open(os.path.join(self.dir_path, self.filen), 'w') as json_file:
            json.dump(self.obj, json_file, indent=2)
