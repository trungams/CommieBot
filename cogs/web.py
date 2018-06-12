#!/usr/bin/python3

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# Web scraping
import requests
from bs4 import BeautifulSoup

class Web():
    def __init__(self, bot):
        self.bot = bot


    @commands.command(pass_context=True)
    async def google(self, ctx, *, query: str):
        '''
        Search and return the first 5 results from Google for query.
        '''
        titles = []
        descriptions = []
        url = 'https://www.google.ca/search?q=%s' % query.replace(' ', '+')
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        r.close()

        stats = soup.find(attrs={'class': 'sd'}).get_text()
        for definition in soup.find_all(attrs={'class': 'g'}, limit=5):
            title = definition.find(attrs={'class': 'r'})
            try:
                titles.append({title.get_text(): 'https://www.google.ca%s' % title.find('a').get('href').replace(')', '%29')})
            except AttributeError:
                continue
            try:
                descriptions.append(definition.find(attrs={'class': 'st'}).get_text())
            except AttributeError:  # There's no text. Only link to images found
                titles[-1][title.get_text()] = 'https://www.google.ca%s' % title.find('a').get('href').replace(')', '%29')
                descriptions.append('See images for %s' % query)

        desc = ''
        for i in range(len(titles)):
            desc += '[**{}**]({})\n{}'.format(list(titles[i].keys())[0], list(titles[i].values())[0], descriptions[i])[0:397] + '...\n\n'

        em = discord.Embed(title='%s#%s'%(ctx.message.author.name, ctx.message.author.discriminator), description=desc, colour=0x3cba54)
        em.set_author(name='Search results from Google for \'%s\':' % query, url=url,
                        icon_url='https://images-ext-1.discordapp.net/external/UsMM0mPPHEKn6WMst8WWG9qMCX_A14JL6Izzr47ucOk/http/i.imgur.com/G46fm8J.png')
        em.set_footer(text=stats)
        await ctx.message.delete()
        await ctx.send(embed=em)


    @commands.command(pass_context=True)
    async def ipa(self, ctx, *, message: str):
        '''
        Return IPA phonetic transcription of message
        '''
        params = {'output_dialect': 'br',
                  'output_style': 'only_tr',
                  'postBracket': '',
                  'preBracket': '',
                  'speech_support': '1',
                  'submit': 'Show+transcription',
                  'text_to_transcribe': message.replace(' ', '+')
                  }

        # headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        #            'Accept-Encoding': 'gzip, deflate, br',
        #            'Accept-Language': 'en-US,en;q=0.5',
        #            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'
        #            }

        r = requests.post('https://tophonetics.com/', data = params)
        soup = BeautifulSoup(r.content, 'html.parser')
        r.close()

        transcribed = soup.find(attrs={'id': 'transcr_output'}).get_text().replace('+', ' ')
        if 'a ' in message: # because of the weird output sometimes
            transcribed = transcribed.replace('eɪ ', 'ə ')
        await ctx.message.delete()
        await ctx.send(transcribed)


def setup(bot):
    bot.add_cog(Web(bot))
