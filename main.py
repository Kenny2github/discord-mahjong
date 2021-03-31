# 3rd-party
from discord.ext import commands
# self
import emojis
from args import cmdargs
from wakeup import wakeup
import config
from loggers import setupClient

client = commands.Bot(cmdargs.prefix)
client.should_stop = False

@client.command()
async def tiles(ctx: commands.Context, *, arg: str):
    await ctx.send(emojis.tiles(arg))

@commands.is_owner()
@client.command()
async def stop(ctx: commands.Context):
    await ctx.message.add_reaction('\N{OK HAND SIGN}')
    client.should_stop = True

setupClient(client)
client.loop.create_task(wakeup(client))
client.run(config.token)
