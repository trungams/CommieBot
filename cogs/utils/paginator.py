#!/usr/bin/python3

import discord
from discord.ext import commands
import asyncio

import math

class Pages():
    def __init__(self, ctx, msg=None, itemList=[], itemPerPage=10, content='some list'):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.user = ctx.author
        self.message = msg
        self.itemList = itemList
        self.itemPerPage = itemPerPage
        self.content = content
        self.embed = discord.Embed()
        self.lastPage = math.ceil(len(self.itemList) / self.itemPerPage)
        self.actions = [('⏪', self.__firstPage),
                        ('◀', self.__prevPage),
                        ('▶', self.__nextPage),
                        ('⏩', self.__lastPage),
                        ('⏹', self.__halt),
                        ('🚮', self.__del)]
        self.currentPage = 1
        self.delete = False


    async def __showPage(self, page):
        self.currentPage = page
        self.embed.title = 'Server: {}'.format(self.guild.name)
        self.embed.colour = 0xff0000
        self.embed.set_author(name=self.content, icon_url='https://cdn.discordapp.com/emojis/417168216994086913.png?v=1')
        self.embed.set_footer(text='Page {} of {} ({} items)'.format(page, self.lastPage, len(itemList)))
        itemIndexStart = self.itemPerPage * (page-1)
        itemIndexEnd = self.itemPerPage * page
        self.embed.description = '\n'.join(self.itemList[itemIndexStart:itemIndexEnd])
        if self.message:
            if self.currentPage == 0:
                try:
                    await self.message.delete()
                    self.message = None
                    return
                except:
                    pass
            else:
                await self.message.edit(embed=self.embed)
                return
        else:
            self.message = await self.channel.send(embed=self.embed, delete_after=1800)
            for (emoji, _) in self.actions:
                await self.message.add_reaction(emoji)
            return


    async def __firstPage(self):
        await self.__showPage(1)


    async def __prevPage(self):
        await self.__showPage(max(1, self.currentPage - 1))


    async def __nextPage(self):
        await self.__showPage(min(self.lastPage, self.currentPage + 1))


    async def __lastPage(self):
        await self.__showPage(self.lastPage)


    async def __halt(self):
        await self.__showPage(0)


    async def __del(self):
        self.delete = True
        await self.__showPage(1)


    def __reactCheck(self, reaction, user):
        if user == self.bot.user:
            return False
        if reaction.message.id != self.message.id:
            return False
        for (emoji, action) in self.actions:
            if reaction.emoji == emoji:
                self.user = user
                self.__turnPage = action
                return True
        return False


    async def paginate(self):
        self.delete = False
        await self.__showPage(self.currentPage)
        while not self.delete and self.message:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=self.__reactCheck)
            except:
                try:
                    self.message.delete()
                except:
                    pass
                finally:
                    break
            await self.__turnPage()
            try:
                await self.message.remove_reaction(reaction, user)
            except:
                pass
