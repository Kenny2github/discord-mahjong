import random
from typing import Tuple, Union
import asyncio
import mahjong
import discord
import emojis

Person = Union[discord.User, discord.Member]
EMOJI_LINE_LIMIT = 16

async def answer(question, answer=None):
    return await asyncio.get_running_loop().run_in_executor(
        None, question.answer, answer)

def str_hand(question: mahjong.UserIO) -> str:
    """Assumes this is the DISCARD_WHAT question"""
    bonuses = emojis.tiles(question.player.bonus)
    if bonuses:
        bonuses += ' '
    shown = ' '.join(map(emojis.tiles, question.shown))
    concealed = emojis.tiles(
        [tile for tile in question.hand if tile is not question.arrived])
    if any(tile is question.arrived for tile in question.hand):
        drawn = emojis.tile(question.arrived)
    else:
        drawn = ''
    return bonuses + shown + concealed + drawn

def str_discard(hand: mahjong.game.Hand) -> str:
    tiles = [emojis.tile(tile) for tile in hand.discarded]
    nums = [emojis.number(i.seat.value + 1) for i in hand.discarders]
    lines = []
    for i in range(0, len(tiles), EMOJI_LINE_LIMIT):
        lines.append(emojis.ZWNJ.join(nums[i:i+EMOJI_LINE_LIMIT]))
        lines.append(emojis.ZWNJ.join(tiles[i:i+EMOJI_LINE_LIMIT]))
    return '\n'.join(lines)

async def play(players: Tuple[Person, ...], bot: discord.ext.commands.Bot):
    game = mahjong.Hand(None)
    prevailing = mahjong.Wind(random.randrange(4))
    question = game.play(prevailing)
    while question is not None:
        if isinstance(question, mahjong.UserIO):
            if question.question == mahjong.Question.READY_Q:
                question = await answer(question)
                continue
            for p in players:
                asyncio.create_task(p.send(embed=discord.Embed(
                    description=str_discard(game)
                )))
            player = players[question.player.seat.value]
            if question.question == mahjong.Question.DISCARD_WHAT:
                asyncio.create_task(player.send(
                    str_hand(question)
                    #embed=discord.Embed(
                    #    description=str_hand(question)
                    #)
                )) # TODO
            return