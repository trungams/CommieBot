#!/usr/bin/python3

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# imports for Db operations
from datetime import datetime
import random, math
import sqlite3
from .utils.paginator import Pages

DB_PATH = './db/Commie.db'

class Quotes():
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True, aliases=['addq'])
    async def addQuote(self, ctx, author: discord.User, *, quote):
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
        await ctx.send('Quote added.')


    @commands.command(pass_context=True, aliases=['q'])
    async def quote(self, ctx, query_1=None, *, query_2=None):
        '''
        Shows a random quote (of a user/contains a certain keywords)
        '''
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        t = None
        mentions = ctx.message.mentions
        server_id = c.execute('SELECT id FROM Servers WHERE Server_id = ?', (ctx.guild.id,)).fetchone()[0]
        if query_1 is None:
            t = (server_id,)
            quotes = c.execute('SELECT * FROM Quotes WHERE Server_id = ?', t).fetchall()
        elif mentions and mentions[0].mention == query_1:
            author_id = mentions[0].id
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
            await ctx.send('Quote not found.')
        else:
            conn.close()
            quote = random.choice(quotes)
            author_id = int(quote[1])
            quote = quote[2]
            author = discord.utils.get(ctx.guild.members, id = author_id)
            author_name = author.display_name if author else 'LEGACY'
            await ctx.send('{} 📣 {}'.format(author_name, quote))


    @commands.command(pass_context=True, aliases=['lq'])
    async def listQuote(self, ctx, author: discord.User=None):
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
            await p.paginate()
            index = 0
            def msgCheck(message):
                try:
                    if (1 <= int(message.content) <= len(quoteList)) and message.author.id == author_id:
                        return True
                    return False
                except ValueError:
                    return False
            while p.delete:
                await ctx.send('Delete option selected. Enter a number to specify which quote you want to delete', delete_after=60)
                try:
                    message = await self.bot.wait_for('message', check=msgCheck, timeout=60)
                except asyncio.TimeoutError:
                    await ctx.send('Command timeout. You may want to run the command again.', delete_after=60)
                    break
                else:
                    index = int(message.content)-1
                    t = (server_id, quoteList[index][1], quoteList[index][2])
                    c.execute('DELETE FROM Quotes WHERE Server_id = ? AND Author_id = ? AND Quote = ?', t)
                    conn.commit()
                    del quoteList[index]
                    ctx.send('Quote deleted', delete_after=60)
                    await message.delete()
                    p.itemList = ['[{}] {}'.format(i+1, quote[2]) for i,quote in zip(range(len(quoteList)),quoteList)]
                    await p.paginate()
            await ctx.message.delete()
            conn.commit()
            conn.close()
        else:
            await ctx.send('No quote found.', delete_after=60)


def setup(bot):
    bot.add_cog(Quotes(bot))
