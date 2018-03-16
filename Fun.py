#!/usr/bin/python3

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# misc imports
import random, math

class Fun():
    def __init__(self, bot):
        self.bot = bot

    # borrowed from Marty
    @commands.command(pass_context=True)
    @asyncio.coroutine
    def mock(self, ctx, *, msg: str=None):
        """mOcKinG sPoNGeBOb
        """
        words = msg.split()
        mix = "".join([(c.upper() if random.randint(0, 1) else c.lower()) for c in msg])
        yield from self.bot.say(mix)
        yield from self.bot.delete_message(ctx.message)

def setup(bot):
    bot.add_cog(Fun(bot))
