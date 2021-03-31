from argparse import RawDescriptionHelpFormatter
from typing import Dict, Union, Optional
import asyncio
from mahjong import Wind
import discord
from discord.ext import commands
from i18n import i18n
from emojis import number, add_ok
from . import thegame

ROOMS = 100

Person = Union[discord.User, discord.Member]

class Room:
    players: Dict[Wind, Optional[Person]]
    ready: Dict[Wind, bool]
    messages: Dict[Wind, Optional[discord.Message]]

    @property
    def seats(self) -> Dict[Person, Wind]:
        return {j: i for i, j in self.players.items() if j is not None}

    @property
    def all_ready(self) -> bool:
        return all(self.ready.values())

    @property
    def full(self) -> bool:
        return not any(p is None for p in self.players.values())

    def __init__(self):
        self.players = {
            Wind.EAST: None,
            Wind.SOUTH: None,
            Wind.WEST: None,
            Wind.NORTH: None,
        }
        self.ready = {
            Wind.EAST: False,
            Wind.SOUTH: False,
            Wind.WEST: False,
            Wind.NORTH: False,
        }
        self.messages = self.players.copy()

    def update(self):
        for wind, player in self.players.items():
            if player is None:
                continue
            desc = '\n'.join(
                i18n(player, 'no-player', number(i+1))
                if p is None
                else i18n(
                    player, 'room-player-' + str(self.ready[i]),
                    number(i+1), p.name)
                for i, p in self.players.items()
            )
            if self.messages[wind] is None:
                asyncio.create_task(self.send(wind, desc))
            else:
                asyncio.create_task(self.messages[wind].edit(
                    embed=discord.Embed(
                        title=i18n(player, 'room-status'),
                        description=desc)))
        if self.all_ready and None not in self.players.values():
            asyncio.create_task(thegame.play(tuple(self.players.values())))

    async def send(self, wind: Wind, desc: str):
        self.messages[wind] = await self.players[wind].send(
            embed=discord.Embed(
                title=i18n(self.players[wind], 'room-status'),
                description=desc))

    def set_ready(self, player: Person, status: bool = True):
        #self.ready[self.seats[player]] = status
        for i in range(4):
            if self.players[i] == player:
                self.ready[i] = status
        self.update()

    def join(self, player: Person) -> Optional[bool]:
        """Return values:

        True - successfully joined
        False - already joined
        None - room full
        """
        if self.has(player):
            pass # return False
        for i in range(4):
            if self.players[i] is None:
                self.players[i] = player
                self.update()
                return True
        return None

    def leave(self, player: Person):
        self.ready[self.seats[player]] = False
        self.messages[self.seats[player]] = None
        self.players[self.seats[player]] = None
        self.update()

    def has(self, player: Person):
        return player in self.seats

class Matchmaking(commands.Cog):
    rooms = [Room() for _ in range(ROOMS)]

    @commands.group(invoke_without_command=True)
    async def mahjong(self, ctx: commands.Context):
        pass

    @mahjong.command()
    async def join(self, ctx: commands.Context):
        for room in self.rooms:
            if room.has(ctx.author):
                #await ctx.send(embed=discord.Embed(
                #    title=i18n(ctx, 'error'),
                #    description=i18n(ctx, 'already-joined'),
                #    color=0xff0000
                #))
                #return
                pass
            if room.full:
                continue
            if not room.join(ctx.author):
                continue
            break

    @mahjong.command()
    async def ready(self, ctx: commands.Context):
        for room in self.rooms:
            if room.has(ctx.author):
                room.set_ready(ctx.author)
                await add_ok(ctx)
                return
        await ctx.send(embed=discord.Embed(
            title=i18n(ctx, 'error'),
            description=i18n(ctx, 'not-joined'),
            color=0xff0000
        ))

    @mahjong.command()
    async def next(self, ctx: commands.Context):
        found = False
        for room in self.rooms:
            if not found:
                if room.has(ctx.author):
                    room.leave(ctx.author)
                    found = True
                continue
            if room.full:
                continue
            if not room.join(ctx.author):
                continue
            break
