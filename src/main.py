import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
__package__ = 'src'
# 3rd-party
import discord
from discord.ext import commands
# self
import emojis
from .args import cmdargs
from .wakeup import wakeup
from . import config
from .loggers import setup_client
from i18n import I18n, load as load_i18n
from .matchmaking import Matchmaking

client = commands.Bot(cmdargs.prefix, activity=discord.Game(',mahjong join'))
client.should_stop = False

@client.command()
async def tiles(ctx: commands.Context, *, arg: str):
    await ctx.send(emojis.tiles(arg))

load_i18n()
client.add_cog(I18n())
client.add_cog(Matchmaking(client))

@commands.is_owner()
@client.command()
async def stop(ctx: commands.Context):
    await emojis.add_ok(ctx)
    client.should_stop = True

setup_client(client)
client.loop.create_task(wakeup(client))
client.run(config.token)
