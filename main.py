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


# import extensions
import cogs
import utils

# Define a list of extensions
extensions = ['cogs.web', 'cogs.db', 'cogs.fun', 'cogs.images']

# Define bot
bot=commands.Bot(command_prefix='>')


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as {}: {}'.format(bot.user.name, bot.user.id))


# 4 functions below are borrowed from Marty
@bot.command(pass_context=True)
@commands.is_owner()
@asyncio.coroutine
def load(ctx, extension_name: str):
    '''
    Load a specific extension.
    '''
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        yield from ctx.send('```{}: {}\n```'.format(type(e).__name__, str(e)))
        return
    yield from ctx.send('{} loaded'.format(extension_name))


@bot.command(pass_context=True)
@commands.is_owner()
@asyncio.coroutine
def unload(ctx, extension_name: str):
    '''
    Unload a specific extension
    '''
    bot.unload_extension(extension_name)
    yield from ctx.send('Unloaded {}.'.format(extension_name))


@bot.command(pass_context=True)
@commands.is_owner()
@asyncio.coroutine
def reset(ctx):
    '''
    Reset bot
    '''
    yield from ctx.send('wait a sec')
    print('Resetting...')
    python = sys.executable
    os.execl(python, python, *sys.argv)


@bot.command(pass_context=True)
@commands.is_owner()
@asyncio.coroutine
def update(ctx):
    '''
    Update bot
    '''
    yield from ctx.send('Commie is evolving...')
    os.system('git pull')


@bot.command(pass_context=True)
@commands.is_owner()
@asyncio.coroutine
def sleep(ctx):
    '''
    It's time to sleep
    '''
    yield from ctx.send('c ya nerds')
    yield from bot.logout()
    print('Bot shut down.')


@bot.command(pass_context=True)
@asyncio.coroutine
def woof(ctx):
    '''
    WHO LET THE DOGS OUT???
    '''
    yield from ctx.send('WOOF WOOF')


@bot.event
@asyncio.coroutine
def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() == 'hi':
        yield from message.channel.send('Bonjour/Hi')
    elif message.content == '?':
        yield from message.channel.send('¿')
    elif message.content.lower() == 'good boy':
        yield from message.channel.send('Thanks!')
    elif 'yee' in message.content:
        yield from message.channel.send('<:yee:414174675837517825>')
    yield from bot.process_commands(message)


# Startup extensions
if __name__ == '__main__':
    for ext in extensions:
        try:
            bot.load_extension(ext)
        except Exception as e:
            print('Failed to load {}\n{}: {}'.format(ext, type(e).__name__, e))


bot.run(os.environ.get('COMMIE_TOKEN'))
