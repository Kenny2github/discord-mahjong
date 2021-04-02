import random
from typing import Tuple, Union
import asyncio
import mahjong
import discord
import emojis
from i18n import i18n

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

async def wait_react(
    msg: discord.Message, bot: discord.ext.commands.Bot,
    allowed: Tuple[str, ...] = None, timeout=10.0
):
    fut = asyncio.get_running_loop().create_future()
    async def listener(payload: discord.RawReactionActionEvent):
        if allowed is not None and str(payload.emoji) not in allowed:
            return
        if payload.message_id == msg.id and payload.user_id != bot.user.id:
            fut.set_result(str(payload.emoji))
    bot.add_listener(listener, 'on_raw_reaction_add')
    bot.add_listener(listener, 'on_raw_reaction_remove')
    r = await fut # await asyncio.wait_for(fut, timeout)
    bot.remove_listener(listener, 'on_raw_reaction_add')
    bot.remove_listener(listener, 'on_raw_reaction_remove')
    return str(r)

async def discard_what(
    question: mahjong.UserIO, player: Person,
    msgs: Tuple[discord.Message, discord.Message],
    bot: discord.ext.commands.Bot
) -> mahjong.Tile:
    msg = await player.send(embed=discord.Embed(
        description=i18n(player, 'q-discard-what')))
    emoji = await wait_react(
        msgs[1], bot, tuple(emojis.LETTERS[:len(question.playable_hand)]))
    background(msg.delete())
    return question.playable_hand[emojis.LETTERS.index(emoji)]

async def meld_from_discard_q(question: mahjong.UserIO, player: Person,
                              bot: discord.ext.commands.Bot):
    meld_types = tuple({type(meld) for meld in question.melds})
    desc = ''
    for i, typ in enumerate(meld_types):
        desc += i18n(player, 'meld-type-' + typ.__name__,
                     emojis.number(i+1)) + '\n'
    desc += i18n(player, 'meld-type-None', emojis.CANCEL)
    foot = i18n(player, 'q-meld-from-discard-q')
    msg = await player.send(
        embed=discord.Embed(description=desc).set_footer(text=foot))
    buttons = tuple(map(emojis.number, range(1, len(meld_types) + 1))) \
        + (emojis.CANCEL,)
    for r in buttons:
        await msg.add_reaction(r)
    emoji = await wait_react(msg, bot, buttons)
    try:
        typ = meld_types[emojis.NUMBERS.index(emoji) - 1]
    except ValueError:
        return None
    melds = [meld for meld in question.melds if isinstance(meld, typ)]
    if len(melds) == 1:
        background(msg.delete())
        return melds[0]
    desc = ''
    for i, meld in enumerate(melds):
        desc += f'{emojis.number(i+1)}: {emojis.tiles(meld)}\n'
    desc += i18n(player, 'meld-type-None', emojis.CANCEL)
    foot = i18n(player, 'q-which-meld')
    background(msg.edit(
        embed=discord.Embed(description=desc).set_footer(text=foot)))
    buttons2 = tuple(map(emojis.number, range(1, len(melds) + 1))) \
        + (emojis.CANCEL,)
    background(msg.remove_reaction(emojis.CANCEL, discord.Object(bot.user.id)))
    for r in buttons2:
        if r in buttons and r != emojis.CANCEL:
            continue # already reacted
        await msg.add_reaction(r)
    emoji = await wait_react(msg, bot, buttons2)
    background(msg.delete())
    try:
        return melds[emojis.NUMBERS.index(emoji) - 1]
    except ValueError:
        return None

async def rob_kong_q(question: mahjong.UserIO, player: Person,
                     bot: discord.ext.commands.Bot):
    if question.question == mahjong.Question.ROB_KONG_Q:
        key = 'q-rob-kong-q'
    else:
        key = 'q-self-draw-q'
    msg = await player.send(embed=discord.Embed(description=i18n(
        player, key, emojis.tiles(question.melds[0]))))
    background(msg.add_reaction(emojis.CHECK))
    background(msg.add_reaction(emojis.CANCEL))
    emoji = await wait_react(msg, bot, (emojis.CHECK, emojis.CANCEL))
    return emoji == emojis.CHECK

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
                tile = await discard_what(question, player, hand_msg, bot)
                question = await answer(question, tile)
            elif question.question in {
                mahjong.Question.MELD_FROM_DISCARD_Q,
                mahjong.Question.SHOW_EKFCP_Q,
                mahjong.Question.SHOW_EKFEP_Q
            }:
                meld = await meld_from_discard_q(question, player, bot)
                question = await answer(question, meld)
            elif question.question in {
                mahjong.Question.ROB_KONG_Q,
                mahjong.Question.SELF_DRAW_Q
            }:
                do = await rob_kong_q(question, player, bot)
                question = await answer(question, do)
            elif question.question == mahjong.Question.WHICH_WU:
                choice = max(question.melds, key=lambda m:
                    mahjong.Wu(melds=m).faan())
                question = await answer(question, choice)
        elif isinstance(question, mahjong.HandEnding):
            question = await answer(question)