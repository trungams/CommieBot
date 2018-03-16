#!/usr/bin/python3

'''
CommieBot for server Commie Nation Shitpost. Written in Python3
Functions: to be updated
'''

#TODO: get lists of user id, channel id, emoji id of a server
#TODO: react bot, delete message, send random messages, manipulating messages (edting, checking reacts)
#TODO: separate to distinct python modules, using extensions afterward to run

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# misc imports for functions
import os, sys, math, random
from datetime import datetime

# Define a list of extensions
extensions = ["Webscrape", "Db", "Fun"]

# Define bot
bot=commands.Bot(command_prefix='>')

#####################################################################
#                                                                   #
#                       SETUP Functions                             #
#                                                                   #
#####################################################################

@bot.event
@asyncio.coroutine
def on_ready():
    print("Logged in as {}: {}".format(bot.user.name, bot.user.id))

# 4 functions below are borrowed from Marty
@bot.command()
@commands.has_any_role("bourgeois")
@asyncio.coroutine
def load(extension_name: str):
    '''
    Load a specific extension.
    '''
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        yield from bot.say("```{}: {}\n```".format(type(e).__name__, str(e)))
        return
    yield from bot.say("{} loaded".format(extension_name))

@bot.command()
@commands.has_any_role("bourgeois")
@asyncio.coroutine
def unload(extension_name: str):
    '''
    Unload a specific extension
    '''
    bot.unload_extension(extension_name)
    yield from bot.say("Unloaded {}.".format(extension_name))

@bot.command()
@commands.has_any_role("bourgeois")
@asyncio.coroutine
def reset():
    yield from bot.say("wait a sec")
    print("Resetting...")
    python = sys.executable
    os.execl(python, python, *sys.argv)

@bot.command()
@commands.has_any_role("bourgeois")
@asyncio.coroutine
def update(ctx):
    # Update the bot by pulling changes from the git repo
    yield from bot.say("Commie is evolving...")
    os.system('git pull')

@bot.command()
@commands.has_any_role("bourgeois")
@asyncio.coroutine
def sleep():
    """It's time to sleep"""
    yield from bot.say("c ya nerds")
    yield from bot.logout()
    print("Bot shut down.")

@bot.command(pass_context=True)
@asyncio.coroutine
def woof(ctx):
    '''
    WHO LET THE DOGS OUT???
    '''
    yield from bot.say("BORK BORK")

@bot.event
@asyncio.coroutine
def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() == "hi":
        yield from bot.send_message(message.channel, "Bonjour/Hi")
    elif message.content.lower() == "i luv u bb":
        yield from bot.send_message(message.channel, "Same")
    elif message.content == "?":
        yield from bot.send_message(message.channel, "¿")
    elif message.content.lower() == "good boy":
        yield from bot.send_message(message.channel, "Thanks!")
    yield from bot.process_commands(message)

# Startup extensions
if __name__ == "__main__":
    for ext in extensions:
        try:
            bot.load_extension(ext)
        except Exception as e:
            print("Failed to load {}\n{}: {}".format(ext, type(e).__name__, e))

#bot.run("NDE5OTE3Njc4NzkxMDk4MzY5.DX_a9g.lDAMkl3demsVcyHFkfQAY6rVymA")
bot.run(os.environ.get("COMMIE_TOKEN"))
