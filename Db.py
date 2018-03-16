#!/usr/bin/python3

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# imports for Db operations
import sqlite3
from datetime import datetime
import random, math

class Database():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @asyncio.coroutine
    def communism(self, ctx):
        f = open("CommiePic.txt")
        piclist = f.read().splitlines()
        yield from self.bot.say(random.choice(piclist)) #TODO: shorten URLs in the list (to clean up msgs)

def setup(bot):
    bot.add_cog(Database(bot))
