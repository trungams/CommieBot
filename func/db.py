#!/usr/bin/python3

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# imports for Db operations
from datetime import datetime
import random, math
import json

class Database():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @asyncio.coroutine
    def communism(self, ctx):
        """
        Send a random commie pic
        """
        f = open("./db/CommPics.txt")
        piclist = f.read().splitlines()
        yield from ctx.send(random.choice(piclist))

    # @commands.command(pass_context=True)
    # @asyncio.coroutine
    # def testmsg(self, ctx):
    #     yield from ctx.send("Say hello!")
    #     def check(m):
    #         return m.content.lower() == "hello"
    #     guess = yield from self.bot.wait_for("message", check=check, timeout=5)
    #     if guess is None:
    #         yield from ctx.send("oops to slow")
    #         return
    #     yield from ctx.send("world!")
    #
    # @commands.is_owner()
    # @commands.command(pass_context=True)
    # @asyncio.coroutine
    # def testreact(self, ctx):
    #     messages = yield from ctx.channel.history(limit=10).flatten()
    #     # msg = yield from ctx.channel.history(limit=2).next()
    #     msg = messages[1]
    #     yield from msg.add_reaction("🅱")
    #     yield from msg.add_reaction("◀")
    #     yield from msg.add_reaction("▶")
    #     yield from msg.add_reaction(":thenkeng:420479362488336395")

def setup(bot):
    bot.add_cog(Database(bot))
