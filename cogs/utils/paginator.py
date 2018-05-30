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


    def __showPage(self, page):
        self.currentPage = page
        self.embed.title = 'Server: {}'.format(self.guild.name)
        self.embed.colour = 0xff0000
        self.embed.set_author(name=self.content, icon_url='https://cdn.discordapp.com/emojis/417168216994086913.png?v=1')
        self.embed.set_footer(text='Page {} of {}'.format(page, self.lastPage))
        itemIndexStart = self.itemPerPage * (page-1)
        itemIndexEnd = self.itemPerPage * page
        self.embed.description = '\n'.join(self.itemList[itemIndexStart:itemIndexEnd])
        if self.message:
            if self.currentPage == 0:
                try:
                    yield from self.message.delete()
                    self.message = None
                    return
                except:
                    pass
            else:
                yield from self.message.edit(embed=self.embed)
                return
        else:
            self.message = yield from self.channel.send(embed=self.embed, delete_after=1800)
            for (emoji, _) in self.actions:
                yield from self.message.add_reaction(emoji)
            return


    def __firstPage(self):
        yield from self.__showPage(1)


    def __prevPage(self):
        yield from self.__showPage(max(1, self.currentPage - 1))


    def __nextPage(self):
        yield from self.__showPage(min(self.lastPage, self.currentPage + 1))


    def __lastPage(self):
        yield from self.__showPage(self.lastPage)


    def __halt(self):
        yield from self.__showPage(0)


    def __del(self):
        self.delete = True
        yield from self.__showPage(1)


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


    def paginate(self):
        self.delete = False
        yield from self.__showPage(self.currentPage)
        while not self.delete and self.message:
            try:
                reaction, user = yield from self.bot.wait_for('reaction_add', check=self.__reactCheck)
            except:
                try:
                    self.message.delete()
                except:
                    pass
                finally:
                    break
            yield from self.__turnPage()
            try:
                yield from self.message.remove_reaction(reaction, user)
            except:
                pass
