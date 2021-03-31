import os
import json

__all__ = ['tile', 'tiles']

with open(os.path.join('emojis', 'emojis.json')) as f:
    EMOJIS = json.load(f)

def tile(path):
    # if path is already string, it's unaffected
    # if it's a Tile, it's cast to a path
    suit, number = str(path).split('/')
    if number.isdecimal():
        number = int(number)
    return EMOJIS[suit][number]

def tiles(paths):
    if not isinstance(paths, (list, tuple)):
        paths = str(paths).split('|')
    return ''.join(tile(path) for path in paths)

OK = '\N{OK HAND SIGN}'