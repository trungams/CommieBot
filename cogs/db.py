#!/usr/bin/python3

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# imports for Db operations
from datetime import datetime
import random, math
import sqlite3

DB_PATH = './db/Commie.db'

class Db():
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def communism(self, ctx):
        '''
        Send a random commie pic
        '''
        f = open('./db/CommPics.txt')
        piclist = f.read().splitlines()
        yield from ctx.send(random.choice(piclist))


    @asyncio.coroutine
    def on_guild_join(self, guild):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        t = (guild.id, guild.name,)
        c.execute('INSERT INTO Servers (Server_id, Server_name) VALUES (?, ?)', t)
        conn.commit()
        conn.close()


    @asyncio.coroutine
    def on_message(self, message):
        if message.author == self.bot.user:
            return
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        server_id = c.execute('SELECT id FROM Servers WHERE Server_id = ?', (message.guild.id,)).fetchone()[0]
        response = ''
        t = (server_id, message.content.lower(),)
        c.execute('SELECT Response FROM Custom_reactions WHERE Server_id = ? AND Trigger = ?', t)
        response = c.fetchone()
        if not response:
            c.execute('SELECT Trigger_part FROM Part_reactions WHERE Server_id = ?', (server_id,))
            triggerList = c.fetchall()
            for trigger in triggerList:
                if trigger[0] in message.content.lower():
                    t = (server_id, trigger[0])
                    c.execute('SELECT Response FROM Part_reactions WHERE Server_id = ? AND Trigger_part = ?', t)
                    response = c.fetchone()
                    break
        if response:
            yield from message.channel.send(response[0])
        conn.close()


    @commands.command(pass_context=True, aliases=['acr', 'addreact'])
    @asyncio.coroutine
    def add_custom_reaction(self, ctx, trigger: str, response: str):
        '''
        Add custom response to a specific message
        '''
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        server_id = c.execute('SELECT id FROM Servers WHERE Server_id = ?', (ctx.guild.id,)).fetchone()[0]
        t = (server_id, trigger.lower(), response,)
        c.execute('INSERT INTO Custom_reactions VALUES (?,?,?)', t)
        conn.commit()
        conn.close()
        yield from ctx.send('Custom reaction created.')


    @add_custom_reaction.error
    @asyncio.coroutine
    def acr_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            yield from ctx.send('Trigger or response messages should not be empty.')
        elif isinstance(error, discord.ext.commands.CommandInvokeError):
            yield from ctx.send('Trigger already exists, please delete the current one to add new or use update command.')


    @commands.command(pass_context=True, aliases=['apr', 'addpartreact'])
    @asyncio.coroutine
    def add_part_reaction(self, ctx, trigger: str, response: str):
        '''
        Custom part reactions. Commie will send a response message if a user's message contains a specific substring. There can only be 10 part reactions per server
        '''
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        server_id = c.execute('SELECT id FROM Servers WHERE Server_id = ?', (ctx.guild.id,)).fetchone()[0]
        t = (server_id, trigger.lower(), response,)
        c.execute('INSERT INTO Part_reactions VALUES (?,?,?)', t)
        conn.commit()
        conn.close()
        yield from ctx.send('Part reaction created.')


    @add_part_reaction.error
    @asyncio.coroutine
    def apr_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            yield from ctx.send('Trigger or response messages should not be empty.')
        elif isinstance(error, discord.ext.commands.CommandInvokeError):
            yield from ctx.send('Reactions limit has been reached, or trigger already exists, please delete the current one to add new or use update command.')


    # @commands.command(pass_context=True)
    # @asyncio.coroutine
    # def testmsg(self, ctx):
    #     yield from ctx.send('Say hello!')
    #     def check(m):
    #         return m.content.lower() == 'hello'
    #     guess = yield from self.bot.wait_for('message', check=check, timeout=5)
    #     if guess is None:
    #         yield from ctx.send('oops to slow')
    #         return
    #     yield from ctx.send('world!')


    # @commands.is_owner()
    # @commands.command(pass_context=True)
    # @asyncio.coroutine
    # def testreact(self, ctx):
    #     messages = yield from ctx.channel.history(limit=10).flatten()
    #     # msg = yield from ctx.channel.history(limit=2).next()
    #     msg = messages[1]
    #     yield from msg.add_reaction('🅱')
    #     yield from msg.add_reaction('◀')
    #     yield from msg.add_reaction('▶')
    #     yield from msg.add_reaction(':thenkeng:420479362488336395')


def setup(bot):
    bot.add_cog(Db(bot))
