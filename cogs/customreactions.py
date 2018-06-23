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

class Db():
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def communism(self, ctx):
        '''
        Send a random commie pic
        '''
        f = open('./db/CommPics.txt')
        piclist = f.read().splitlines()
        await ctx.send(random.choice(piclist))


    async def on_message(self, message):
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
            await message.channel.send(response[0])
        conn.close()


    @commands.command(aliases=['acr', 'addreact'])
    async def addCustomReaction(self, ctx, trigger: str, response: str):
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
        await ctx.send('Custom reaction created.')


    @addCustomReaction.error
    async def acrError(self, ctx, error):
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            await ctx.send('Trigger or response messages should not be empty.', delete_after=60)
        elif isinstance(error, discord.ext.commands.CommandInvokeError):
            await ctx.send('Reactions limit has been reached, or trigger already exists, please delete the current one to add new or use update command.', delete_after=60)


    @commands.command(aliases=['lcr', 'listcustomreact'])
    @commands.cooldown(rate=1, per=120)
    async def listCustomReaction(self, ctx):
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
            await p.paginate()

            index = 0
            def msgCheck(message):
                try:
                    if (1 <= int(message.content) <= len(cr_list)) and message.author == p.user:
                        return True
                    return False
                except ValueError:
                    return False

            while p.delete:
                await ctx.send('Delete option selected. Enter a number to specify which reaction you want to delete.', delete_after=60)
                try:
                    message = await self.bot.wait_for('message', check=msgCheck, timeout=60)
                except asyncio.TimeoutError:
                    await ctx.send('Command timeout. You may want to run the command again.', delete_after=60)
                    break
                else:
                    index = int(message.content)-1
                    t = (server_id, cr_list[index][0], )
                    c.execute('DELETE FROM Custom_reactions WHERE Server_id = ? AND Trigger = ?', t)
                    conn.commit()
                    del cr_list[index]
                    await ctx.send('Custom reaction deleted.')
                    await message.delete()
                    # p.itemList = [f'[{i+1}] **{cr[0]}**\n\t→ {cr[1]}' for i,cr in zip(range(len(cr_list)),cr_list)]
                    p.itemList = ['[{}] **{}**\n\t→ {}'.format(i+1, cr[0], cr[1]) for i,cr in zip(range(len(cr_list)),cr_list)]
                    await p.paginate()
            await ctx.message.delete()
            conn.commit()
            conn.close()
        else:
            await ctx.send('No part reaction found.', delete_after=60)


    @listCustomReaction.error
    async def lcrError(self, ctx, error):
        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            await ctx.send('Command is on cooldown. Please chill', delete_after=90)


    @commands.command(aliases=['apr', 'addpartreact'])
    async def addPartReaction(self, ctx, trigger: str, response: str):
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
        await ctx.send('Part reaction created.')


    @addPartReaction.error
    async def aprError(self, ctx, error):
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            await ctx.send('Trigger or response messages should not be empty.', delete_after=60)
        elif isinstance(error, discord.ext.commands.CommandInvokeError):
            await ctx.send('Reactions limit has been reached, or trigger already exists, please delete the current one to add new or use update command.', delete_after=60)


    @commands.command(aliases=['lpr', 'listpartreact'])
    @commands.cooldown(rate=1, per=120)
    async def listPartReaction(self, ctx):
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
            await p.paginate()

            index = 0
            def msgCheck(message):
                try:
                    if (1 <= int(message.content) <= len(pr_list)) and message.author == p.user:
                        return True
                    return False
                except ValueError:
                    return False

            while p.delete:
                await ctx.send('Delete option selected. Enter a number to specify which reaction you want to delete.', delete_after=60)
                try:
                    message = await self.bot.wait_for('message', check=msgCheck, timeout=60)
                except asyncio.TimeoutError:
                    await ctx.send('Command timeout. You may want to run the command again.', delete_after=60)
                    break
                else:
                    index = int(message.content)-1
                    t = (server_id, pr_list[index][0], )
                    c.execute('DELETE FROM Part_reactions WHERE Server_id = ? AND Trigger_part = ?', t)
                    conn.commit()
                    del pr_list[index]
                    await ctx.send('Part reaction deleted.')
                    await message.delete()
                    # p.itemList = [f'[{i+1}] **{pr[0]}**\n\t→ {pr[1]}' for i,pr in zip(range(len(pr_list)),pr_list)]
                    p.itemList = ['[{}] **{}**\n\t→ {}'.format(i+1, pr[0], pr[1]) for i,pr in zip(range(len(pr_list)),pr_list)]
                    await p.paginate()
            await ctx.message.delete()
            conn.commit()
            conn.close()
        else:
            await ctx.send('No part reaction found.', delete_after=60)


    @listPartReaction.error
    async def lprError(self, ctx, error):
        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            await ctx.send('Command is on cooldown. Please chill', delete_after=90)


def setup(bot):
    bot.add_cog(Db(bot))
