# low-level
import time
# mid-level
import logging
# high-level
import traceback
# 3rd-party
import discord
from discord.ext import commands
# self
from args import cmdargs

if cmdargs.stdout:
    handler = logging.StreamHandler()
else:
    handler = logging.FileHandler(
        time.strftime('logs/%Y-%m-%d %H-%M-%S.log'),
        mode='w', encoding='utf8', delay=True)
handler.setFormatter(logging.Formatter(
    fmt='{levelname} {asctime} {name}: {message}',
    datefmt='%Y-%m-%dT%H:%M:%SZ',
    style='{'
))

logging.basicConfig(handlers=[handler])
LOGLEVEL = logging.DEBUG if cmdargs.v else logging.INFO

stdlogger = logging.getLogger('mahjong.(std)')
stdlogger.setLevel(LOGLEVEL)

def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOGLEVEL)
    return logger

async def on_command_error(ctx, exc):
    stdlogger.error(
        'Ignoring exception in command %s: %s %s',
        ctx.command, type(exc).__name__, exc)
    if hasattr(ctx.command, 'on_error'):
        return
    cog = ctx.cog
    if cog:
        if commands.Cog._get_overridden_method(cog.cog_command_error) is not None:
            return
    if isinstance(exc, (
        commands.BotMissingPermissions,
        commands.MissingPermissions,
        commands.MissingRequiredArgument,
        commands.BadArgument,
        commands.CommandOnCooldown,
    )):
        return await ctx.send(embed=discord.Embed(
            title=('error',),
            description=str(exc),
            color=0xff0000
        ))
    if isinstance(exc, (
        commands.CheckFailure,
        commands.CommandNotFound,
        commands.TooManyArguments,
        discord.Forbidden
    )):
        return
    stdlogger.error(''.join(traceback.format_exception(
        type(exc), exc, exc.__traceback__
    )))

async def before_invoke(ctx):
    stdlogger.info(
        '%s\t(%s) running %s%s',
        ctx.author, ctx.author.id, ctx.prefix, ctx.command)

def setup_client(client: commands.Bot):
    client.event(on_command_error)
    client.before_invoke(before_invoke)