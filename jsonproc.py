import json
import pandas as pd
import os

class Jsonobject:

    def __init__(self, json_obj):
        self.json_object = json_obj

    def get(sefl, key):
        pass

class Csvobject:
    pass

class Xlsobject:
    pass

class Reader:

    def __init__(self, filename, type_of_file):

        self.filename = filename
        if not os.path.isfile(self.filename):
            raise IOError("File {} does not exist".format(self.filename))
        self.type_of_file = type_of_file

    def read_file(sefl.filename):
        if type_of_file == "json":
            with open(self.filename, 'r') as f:
                self.json_obj = json.load(f)
        elif type_of_file == "xls":
        elif type_of_file == "csv":

class Writer:
    pass

def main():
    pass

if __name__ == "__main__":
    main()
