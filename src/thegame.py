import random
from typing import Tuple, Union
import asyncio
import mahjong
import discord
import emojis

Person = Union[discord.User, discord.Member]
EMOJI_LINE_LIMIT = 12
SPACE = '  '

background = asyncio.create_task

async def answer(question, answer=None):
    return await asyncio.get_running_loop().run_in_executor(
        None, question.answer, answer)

def str_hand(question: mahjong.UserIO) -> Tuple[str, str]:
    """Assumes this is the DISCARD_WHAT question"""
    labels = emojis.BLANK * len(question.player.bonus)
    if question.player.bonus:
        labels += SPACE
    labels += emojis.BLANK.join(emojis.BLANK * 3 for _ in question.shown)
    if question.shown:
        labels += SPACE
    labels += ''.join(i for i, _ in zip(emojis.LETTERS, question.playable_hand))
    bonuses = emojis.tiles(question.player.bonus)
    if bonuses:
        bonuses += SPACE
    shown = emojis.BLANK.join(map(emojis.tiles, question.shown))
    if shown:
        shown += SPACE
    concealed = emojis.tiles(question.playable_hand)
    if any(tile is question.arrived for tile in question.hand):
        drawn = SPACE + emojis.tile(question.arrived)
        labels += SPACE + emojis.LETTERS[len(question.playable_hand)]
    else:
        drawn = ''
    return labels, bonuses + shown + concealed + drawn

def str_discard(hand: mahjong.game.Hand) -> str:
    tiles = [emojis.tile(tile) for tile in hand.discarded]
    nums = [emojis.number(i.seat.value + 1) for i in hand.discarders]
    lines = []
    for i in range(0, len(tiles), EMOJI_LINE_LIMIT):
        lines.append(emojis.ZWNJ.join(nums[i:i+EMOJI_LINE_LIMIT]))
        lines.append(emojis.ZWNJ.join(tiles[i:i+EMOJI_LINE_LIMIT]))
    return '\n'.join(lines)

async def update_discard(msgs: Tuple[discord.Message, ...],
                         game: mahjong.Hand):
    await asyncio.gather(*(m.edit(content=str_discard(game)) for m in msgs))

async def update_hand(msgs: Tuple[discord.Message, discord.Message],
                      question: mahjong.UserIO):
    await asyncio.gather(*(
        msg.edit(content=c) for msg, c in zip(msgs, str_hand(question))))

async def react_hand(player: Person):
    msg1 = await player.send(emojis.ZWNJ)
    msg2 = await player.send(emojis.ZWNJ)
    for i in emojis.LETTERS[:14]:
        await msg2.add_reaction(i)
    return (msg1, msg2)

async def play(players: Tuple[Person, ...], bot: discord.ext.commands.Bot):
    game = mahjong.Hand(None)
    prevailing = mahjong.Wind(random.randrange(4))
    question = game.play(prevailing)
    discard_msgs: Tuple[discord.Message, ...] = await asyncio.gather(*(
        p.send(embed=discord.Embed()) for p in players))
    hand_msgs: Tuple[discord.Message, ...] = await asyncio.gather(*(
        react_hand(p) for p in players))
    while question is not None:
        if isinstance(question, mahjong.UserIO):
            if question.question == mahjong.Question.READY_Q:
                question = await answer(question)
                continue
            background(update_discard(discard_msgs, game))
            player = players[question.player.seat.value]
            hand_msg = hand_msgs[question.player.seat.value]
            background(update_hand(hand_msg, question))
            if question.question == mahjong.Question.DISCARD_WHAT:
                asyncio.create_task(player.send(
                    str_hand(question)
                    #embed=discord.Embed(
                    #    description=str_hand(question)
                    #)
                )) # TODO
            return