import os
import json
from typing import Dict
import asyncio
import discord
from discord.ext import commands
import emojis
from src.loggers import getLogger

STRINGS: Dict[str, Dict[str, str]] = {}
I18N_ROOT = os.path.dirname(os.path.abspath(__file__))

logger = getLogger('mahjong.i18n')

def load():
    root = I18N_ROOT
    for i in os.listdir(root):
        if not i.endswith('.json'):
            continue
        with open(os.path.join(root, i)) as f:
            STRINGS[i[:-len('.json')]] = json.load(f)
    logger.debug('Loaded strings: %s', ', '.join(STRINGS.keys()))

def i18n(ctx: commands.Context, key: str, *args: str):
    idkey = getattr(ctx, 'author', ctx).id
    lang = STRINGS['users'].setdefault(str(idkey), 'en')
    default = ", ".join(f'{{{i}}}' for i, arg in enumerate(args))
    string = STRINGS[lang].get(key, f'|{key}: {default}|')
    return string.format(*args)

class I18n(commands.Cog):

    lock = asyncio.Lock()

    @commands.group(name='i18n', invoke_without_command=True)
    async def _i18n(self, ctx: commands.Context):
        pass

    @commands.is_owner()
    @_i18n.command()
    async def reload(self, ctx: commands.Context):
        load()
        await emojis.add_ok(ctx)

    @commands.command()
    async def lang(self, ctx: commands.Context, langcode: str = None):
        langs = ', '.join(i for i in STRINGS if i != 'users')
        if langcode is None:
            await ctx.send(embed=discord.Embed(
                title=i18n(ctx, 'current-lang',
                           STRINGS['users'].get(str(ctx.author.id), 'None')),
                description=i18n(ctx, 'existing-langs', langs, ctx.prefix),
                color=0x55acee
            ))
            return
        if langcode not in STRINGS or langcode == 'users':
            await ctx.send(embed=discord.Embed(
                title=i18n(ctx, 'error'),
                description=i18n(ctx, 'invalid-lang', langcode, langs),
                color=0xff0000
            ))
            return
        STRINGS['users'][str(ctx.author.id)] = langcode
        async with self.lock:
            with open(os.path.join(I18N_ROOT, 'users.json'), 'w') as f:
                json.dump(STRINGS['users'], f)
            logger.debug('Set lang for %s to %s', ctx.author.id, langcode)
        await emojis.add_ok(ctx)