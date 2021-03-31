import os
import json
from discord.ext.commands import Context

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

def tiles(paths, *, sep: str = ''):
    if not isinstance(paths, (list, tuple)):
        paths = str(paths).split('|')
    return sep.join(tile(path) for path in paths)

OK = '\N{OK HAND SIGN}'
NUMBERS = """<:0_number:821299270829080606>
<:1_number:821299269381390337>
<:2_number:821299269829918740>
<:3_number:821299269775917067>
<:4_number:821299269994283030>
<:5_number:821299270119981086>
<:6_number:821299269910790164>
<:7_number:821299270182895616>
<:8_number:821299269994283018>
<:9_number:821299269998739496>""".splitlines()
ZWNJ = '\N{ZERO WIDTH NON-JOINER}'

async def add_ok(ctx: Context):
    await ctx.message.add_reaction(OK)

def number(num: int, *, sep: str = '') -> str:
    return sep.join(NUMBERS[int(i)] for i in str(int(num)))