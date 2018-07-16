#!/usr/bin/python3

'''
CommieBot for server Commie Nation Shitpost. Written in Python3
Functions: to be updated
'''

#TODO: get lists of user id, channel id, emoji id of a server
#TODO: react bot, delete message, send random messages


# imports for Discord
import discord
from discord.ext import commands
import asyncio
import logging


# misc imports for functions
import os, sys, math, random
from datetime import datetime
import sqlite3


# Define a list of extensions
extensions = [
    'cogs.web',
    'cogs.customreactions',
    'cogs.fun',
    'cogs.images',
    'cogs.quotes',
    'cogs.reminder'
]
DB_PATH = './db/Commie.db'

# Define bot
bot = commands.Bot(command_prefix='!')


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


@bot.event
async def on_ready():
    print('Logged in as {}: {}'.format(bot.user.name, bot.user.id))


@bot.event
async def on_guild_join():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    t = (guild.id, guild.name,)
    c.execute('INSERT INTO Servers (Server_id, Server_name) VALUES (?, ?)', t)
    conn.commit()
    conn.close()


# 4 functions below are borrowed from Marty
@bot.command()
@commands.is_owner()
async def load(ctx, extension_name: str):
    '''
    Load a specific extension.
    '''
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        await ctx.send('```{}: {}\n```'.format(type(e).__name__, str(e)))
        return
    await ctx.send('{} loaded'.format(extension_name))


@bot.command()
@commands.is_owner()
async def unload(ctx, extension_name: str):
    '''
    Unload a specific extension
    '''
    bot.unload_extension(extension_name)
    await ctx.send('Unloaded {}.'.format(extension_name))


@bot.command()
@commands.is_owner()
async def reset(ctx):
    '''
    Reset bot
    '''
    await ctx.send('wait a sec')
    print('Resetting...')
    python = sys.executable
    os.execl(python, python, *sys.argv)


@bot.command()
@commands.is_owner()
async def update(ctx):
    '''
    Update bot
    '''
    os.system('git pull')
    await ctx.send('Updated!')


@bot.command()
@commands.is_owner()
async def sleep(ctx):
    '''
    It's time to sleep
    '''
    await ctx.send('c ya nerds')
    await bot.logout()
    print('Bot shut down.')


@bot.command()
async def woof(ctx):
    '''
    WHO LET THE DOGS OUT???
    '''
    await ctx.send('WOOF WOOF')


# Startup extensions
if __name__ == '__main__':
    for ext in extensions:
        try:
            bot.load_extension(ext)
        except Exception as e:
            print('Failed to load {}\n{}: {}'.format(ext, type(e).__name__, e))


bot.run(os.environ.get('COMMIE_TOKEN'))
