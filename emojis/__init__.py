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
LETTERS = """<:a_letter:821296270400028692>
<:b_letter:821296270714994718>
<:c_letter:821296270396096552>
<:d_letter:821296270441840680>
<:e_letter:821296270500823060>
<:f_letter:821296270530314241>
<:g_letter:821296270390984724>
<:h_letter:821296270382727199>
<:i_letter:821296270413004812>
<:j_letter:821296270777909248>
<:k_letter:827532148583694377>
<:l_letter:827532148533755924>
<:m_letter:827532148465598464>
<:n_letter:827532148844134440>""".splitlines()
SPACE = '<:__letter:821296269913227265>'
ZWNJ = '\N{ZERO WIDTH NON-JOINER}'
CANCEL = '\N{NEGATIVE SQUARED CROSS MARK}'

async def add_ok(ctx: Context):
    await ctx.message.add_reaction(OK)

def number(num: int, *, sep: str = '') -> str:
    return sep.join(NUMBERS[int(i)] for i in str(int(num)))

def letter(lttr: str, *, sep: str = '') -> str:
    return sep.join(
        LETTERS[ord(i.casefold()) - ord('a')]
        if i != ' ' else SPACE
        for i in str(lttr))