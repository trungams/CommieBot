#!/usr/bin/python3

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# imports for Db operations
from datetime import datetime
import random, math
import sqlite3
import time
from .utils.paginator import Pages

DB_PATH = './db/Commie.db'

#TODO: quote commands

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
    def addCustomReaction(self, ctx, trigger: str, response: str):
        '''
        Add custom response to a specific message. Limit to 100 custom reactions per server.
        '''
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        server_id = c.execute('SELECT id FROM Servers WHERE Server_id = ?', (ctx.guild.id,)).fetchone()[0]
        t = (server_id, trigger.lower(), response,)
        c.execute('INSERT INTO Custom_reactions VALUES (?,?,?)', t)
        conn.commit()
        conn.close()
        yield from ctx.send('Custom reaction created.')


    @addCustomReaction.error
    @asyncio.coroutine
    def acrError(self, ctx, error):
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            yield from ctx.send('Trigger or response messages should not be empty.', delete_after=60)
        elif isinstance(error, discord.ext.commands.CommandInvokeError):
            yield from ctx.send('Reactions limit has been reached, or trigger already exists, please delete the current one to add new or use update command.', delete_after=60)


    @commands.command(pass_context=True, aliases=['lcr', 'listcustomreact'])
    @commands.cooldown(rate=1, per=120)
    @asyncio.coroutine
    def listCustomReaction(self, ctx):
        '''
        List all custom reactions of the server
        '''
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        server_id = c.execute('SELECT id FROM Servers WHERE Server_id = ?', (ctx.guild.id,)).fetchone()[0]
        c.execute('SELECT Trigger, Response FROM Custom_reactions WHERE Server_id = ?', (server_id,))
        cr_list = c.fetchall()
        if cr_list:
            # cr_text = [f'[{i+1}] **{cr[0]}**\n\t→ {cr[1]}' for i,cr in zip(range(len(cr_list)),cr_list)]
            cr_text = ['[{}] **{}**\n\t→ {}'.format(i+1, cr[0], cr[1]) for i,cr in zip(range(len(cr_list)),cr_list)]
            p = Pages(ctx, itemList=cr_text, content='Custom reaction list')
            yield from p.paginate()

            index = 0
            def msgCheck(message):
                try:
                    if (1 <= int(message.content) <= len(cr_list)) and message.author == p.user:
                        return True
                    return False
                except ValueError:
                    return False

            while p.delete:
                yield from ctx.send('Delete option selected. Enter a number to specify which reaction you want to delete.', delete_after=60)
                try:
                    message = yield from self.bot.wait_for('message', check=msgCheck, timeout=60)
                except asyncio.TimeoutError:
                    yield from ctx.send('Command timeout. You may want to run the command again.', delete_after=60)
                    break
                else:
                    index = int(message.content)-1
                    t = (server_id, cr_list[index][0], )
                    c.execute('DELETE FROM Custom_reactions WHERE Server_id = ? AND Trigger = ?', t)
                    conn.commit()
                    del cr_list[index]
                    yield from ctx.send('Custom reaction deleted.')
                    yield from message.delete()
                    # p.itemList = [f'[{i+1}] **{cr[0]}**\n\t→ {cr[1]}' for i,cr in zip(range(len(cr_list)),cr_list)]
                    p.itemList = ['[{}] **{}**\n\t→ {}'.format(i+1, cr[0], cr[1]) for i,cr in zip(range(len(cr_list)),cr_list)]
                    yield from p.paginate()
            yield from ctx.message.delete()
            conn.commit()
            conn.close()
        else:
            yield from ctx.send('No part reaction found.', delete_after=60)


    @listCustomReaction.error
    @asyncio.coroutine
    def lcrError(self, ctx, error):
        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            yield from ctx.send('Command is on cooldown. Please chill', delete_after=90)


    @commands.command(pass_context=True, aliases=['apr', 'addpartreact'])
    @asyncio.coroutine
    def addPartReaction(self, ctx, trigger: str, response: str):
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


    @addPartReaction.error
    @asyncio.coroutine
    def aprError(self, ctx, error):
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            yield from ctx.send('Trigger or response messages should not be empty.', delete_after=60)
        elif isinstance(error, discord.ext.commands.CommandInvokeError):
            yield from ctx.send('Reactions limit has been reached, or trigger already exists, please delete the current one to add new or use update command.', delete_after=60)


    @commands.command(pass_context=True, aliases=['lpr', 'listpartreact'])
    @commands.cooldown(rate=1, per=120)
    @asyncio.coroutine
    def listPartReaction(self, ctx):
        '''
        List all custom part reactions of the server
        '''
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        server_id = c.execute('SELECT id FROM Servers WHERE Server_id = ?', (ctx.guild.id,)).fetchone()[0]
        c.execute('SELECT Trigger_part, Response FROM Part_reactions WHERE Server_id = ?', (server_id,))
        pr_list = c.fetchall()
        if pr_list:
            # pr_text = [f'[{i+1}] **{pr[0]}**\n\t→ {pr[1]}' for i,pr in zip(range(len(pr_list)),pr_list)]
            pr_text = ['[{}] **{}**\n\t→ {}'.format(i+1, pr[0], pr[1]) for i,pr in zip(range(len(pr_list)),pr_list)]
            p = Pages(ctx, itemList=pr_text, content='Part reaction list')
            yield from p.paginate()

            index = 0
            def msgCheck(message):
                try:
                    if (1 <= int(message.content) <= len(pr_list)) and message.author == p.user:
                        return True
                    return False
                except ValueError:
                    return False

            while p.delete:
                yield from ctx.send('Delete option selected. Enter a number to specify which reaction you want to delete.', delete_after=60)
                try:
                    message = yield from self.bot.wait_for('message', check=msgCheck, timeout=60)
                except asyncio.TimeoutError:
                    yield from ctx.send('Command timeout. You may want to run the command again.', delete_after=60)
                    break
                else:
                    index = int(message.content)-1
                    t = (server_id, pr_list[index][0], )
                    c.execute('DELETE FROM Part_reactions WHERE Server_id = ? AND Trigger_part = ?', t)
                    conn.commit()
                    del pr_list[index]
                    yield from ctx.send('Part reaction deleted.')
                    yield from message.delete()
                    # p.itemList = [f'[{i+1}] **{pr[0]}**\n\t→ {pr[1]}' for i,pr in zip(range(len(pr_list)),pr_list)]
                    p.itemList = ['[{}] **{}**\n\t→ {}'.format(i+1, pr[0], pr[1]) for i,pr in zip(range(len(pr_list)),pr_list)]
                    yield from p.paginate()
            yield from ctx.message.delete()
            conn.commit()
            conn.close()
        else:
            yield from ctx.send('No part reaction found.', delete_after=60)


    @listPartReaction.error
    @asyncio.coroutine
    def lprError(self, ctx, error):
        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            yield from ctx.send('Command is on cooldown. Please chill', delete_after=90)


    @commands.command(pass_context=True, aliases=['addq'])
    @asyncio.coroutine
    def addQuote(self, ctx, author: discord.User, *, quote):
        '''
        Another way to pin messages
        '''
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        author_id = author.id
        server_id = c.execute('SELECT id FROM Servers WHERE Server_id = ?', (ctx.guild.id,)).fetchone()[0]
        t = (server_id, author_id, quote,)
        c.execute('INSERT INTO Quotes VALUES (?,?,?)', t)
        conn.commit()
        conn.close()
        yield from ctx.send('Quote added.')


    @commands.command(pass_context=True, aliases=['q'])
    @asyncio.coroutine
    def quote(self, ctx, query_1=None, *, query_2=None):
        '''
        Shows a random quote (of a user/contains a certain keywords)
        '''
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        t = None
        server_id = c.execute('SELECT id FROM Servers WHERE Server_id = ?', (ctx.guild.id,)).fetchone()[0]
        if query_1 is None:
            t = (server_id,)
            quotes = c.execute('SELECT * FROM Quotes WHERE Server_id = ?', t).fetchall()
        elif isinstance(query_1, discord.User):
            author_id = query_1.id
            if query_2 is None:
                t = (server_id, author_id, '%%',)
            else:
                t = (server_id, author_id, '%' + query_2 + '%',)
            c.execute('SELECT * FROM Quotes WHERE Server_id = ? AND Author_id = ? AND Quote LIKE ?', t)
            quotes = c.fetchall()
        else:
            query = query_1 if query_2 is None else query_1 + ' ' + query_2
            t = (server_id, '%' + query + '%',)
            c.execute('SELECT * FROM Quotes WHERE Server_id = ? AND Quote LIKE ?', t)
            quotes = c.fetchall()
        if not quotes:
            conn.close()
            yield from ctx.send('Quote not found.')
        else:
            conn.close()
            quote = random.choice(quotes)
            author_id = int(quote[1])
            quote = quote[2]
            author = discord.utils.get(ctx.guild.members, id = author_id)
            author_name = author.display_name
            yield from ctx.send('{} 📣 {}'.format(author_name, quote))


    @commands.command(pass_context=True, aliases=['lq'])
    @asyncio.coroutine
    def listQuote(self, ctx, author: discord.User=None):
        '''
        List quotes
        '''
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        quoteAuthor = author if author else ctx.message.author
        author_id = quoteAuthor.id
        server_id = c.execute('SELECT id FROM Servers WHERE Server_id = ?', (ctx.guild.id,)).fetchone()[0]
        t = (server_id, author_id,)
        c.execute('SELECT * FROM Quotes WHERE Server_id = ? AND Author_id = ?', t)
        quoteList = c.fetchall()
        if quoteList:
            quoteListText = ['[{}] {}'.format(i+1, quote[2]) for i,quote in zip(range(len(quoteList)),quoteList)]
            p = Pages(ctx, itemList=quoteListText, content='List quotes')
            yield from p.paginate()
            index = 0
            def msgCheck(message):
                try:
                    if (1 <= int(message.content) <= len(quoteList)) and message.author.id == author_id:
                        return True
                    return False
                except ValueError:
                    return False
            while p.delete:
                yield from ctx.send('Delete option selected. Enter a number to specify which quote you want to delete', delete_after=60)
                try:
                    message = yield from self.bot.wait_for('message', check=msgCheck, timeout=60)
                except asyncio.TimeoutError:
                    yield from ctx.send('Command timeout. You may want to run the command again.', delete_after=60)
                    break
                else:
                    index = int(message.content)-1
                    t = (server_id, quoteList[index][1], quoteList[index][2])
                    c.execute('DELETE FROM Quotes WHERE Server_id = ? AND Author_id = ? AND Quote = ?', t)
                    conn.commit()
                    del quoteList[index]
                    ctx.send('Quote deleted', delete_after=60)
                    yield from message.delete()
                    p.itemList = ['[{}] {}'.format(i+1, quote[2]) for i,quote in zip(range(len(quoteList)),quoteList)]
                    yield from p.paginate()
            yield from ctx.message.delete()
            conn.commit()
            conn.close()
        else:
            yield from ctx.send('No quote found.', delete_after=60)


def setup(bot):
    bot.add_cog(Db(bot))
