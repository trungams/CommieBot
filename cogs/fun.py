#!/usr/bin/python3

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# misc imports
import os, random, math

class Fun():
    def __init__(self, bot):
        self.bot = bot


    # borrowed from Marty
    @commands.command(pass_context=True)
    @asyncio.coroutine
    def mock(self, ctx, *, message: str=None):
        '''
        mOcKinG sPoNGeBOb
        '''
        mix = ''.join([(c.upper() if random.randint(0, 1) else c.lower()) for c in message])
        yield from ctx.send(mix)
        yield from ctx.message.delete()


    @commands.command(pass_context=True, aliases=['aes', 'vaporwave', 'vapor'])
    @asyncio.coroutine
    def aesthetic(self, ctx, *, message):
        '''
        ａｅｓｔｈｅｔｉｃ
        '''
        aes_dict = {' ':'　','a':'ａ','b':'ｂ','c':'ｃ','d':'ｄ','e':'ｅ','f':'ｆ','g':'ｇ','h':'ｈ','i':'ｉ','j':'ｊ','k':'ｋ','l':'ｌ','m':'ｍ',
					'n':'ｎ','o':'ｏ','p':'ｐ','q':'ｑ','r':'ｒ','s':'ｓ','t':'ｔ','u':'ｕ','v':'ｖ','w':'ｗ','x':'ｘ','y':'ｙ','z':'ｚ',
					'A':'Ａ','B':'Ｂ','C':'Ｃ','D':'Ｄ','E':'Ｅ','F':'Ｆ','G':'Ｇ','H':'Ｈ','I':'Ｉ','J':'Ｊ','K':'Ｋ','L':'Ｌ','M':'Ｍ',
					'N':'Ｎ','O':'Ｏ','P':'Ｐ','Q':'Ｑ','R':'Ｒ','S':'Ｓ','T':'Ｔ','U':'Ｕ','V':'Ｖ','W':'Ｗ','X':'Ｘ','Y':'Ｙ','Z':'Ｚ',
					'1':'１','2':'２','3':'３','4':'４','5':'５','6':'６','7':'７','8':'８','9':'９','0':'０'}
        aesthetics = ''.join([(aes_dict[c] if aes_dict.get(c) else c) for c in message])
        yield from ctx.message.delete()
        yield from ctx.send(aesthetics)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def thicc(self, ctx, *, message):
        '''
        乇乂丅尺卂 丅卄工匚匚
        '''
        thicc_dict = {'a':'卂','b':'乃','c':'匚','d':'刀','e':'乇','f':'下','g':'厶','h':'卄',
						'i':'工','j':'丁','k':'长','l':'乚','m':'从','n':'𠘨','o':'口','p':'尸',
						'q':'㔿','r':'尺','s':'丂','t':'丅','u':'凵','v':'リ','w':'山','x':'乂','y':'丫','z':'乙'}
        extra_thicc = ''.join([(thicc_dict[c] if thicc_dict.get(c) else c) for c in message.lower()])
        yield from ctx.message.delete()
        yield from ctx.send(extra_thicc)


def setup(bot):
    bot.add_cog(Fun(bot))
