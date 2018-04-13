#!/usr/bin/python3

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# misc imports
import os, random, math
from PIL import Image, ImageEnhance, ImageFilter

class Fun():
    def __init__(self, bot):
        self.bot = bot

    # borrowed from Marty
    @commands.command(pass_context=True)
    @asyncio.coroutine
    def mock(self, ctx, *, message: str=None):
        """
        mOcKinG sPoNGeBOb
        """
        mix = "".join([(c.upper() if random.randint(0, 1) else c.lower()) for c in message])
        yield from ctx.send(mix)
        yield from ctx.message.delete()

    @commands.command(pass_context=True, aliases=["aes", "vaporwave", "vapor"])
    @asyncio.coroutine
    def aesthetic(self, ctx, *, message):
        """
        ａｅｓｔｈｅｔｉｃ
        """
        aes_dict = {" ":"　","a":"ａ","b":"ｂ","c":"ｃ","d":"ｄ","e":"ｅ","f":"ｆ","g":"ｇ","h":"ｈ","i":"ｉ","j":"ｊ","k":"ｋ","l":"ｌ","m":"ｍ","n":"ｎ","o":"ｏ","p":"ｐ","q":"ｑ","r":"ｒ","s":"ｓ","t":"ｔ","u":"ｕ","v":"ｖ","w":"ｗ","x":"ｘ","y":"ｙ","z":"ｚ","A":"Ａ","B":"Ｂ","C":"Ｃ","D":"Ｄ","E":"Ｅ","F":"Ｆ","G":"Ｇ","H":"Ｈ","I":"Ｉ","J":"Ｊ","K":"Ｋ","L":"Ｌ","M":"Ｍ","N":"Ｎ","O":"Ｏ","P":"Ｐ","Q":"Ｑ","R":"Ｒ","S":"Ｓ","T":"Ｔ","U":"Ｕ","V":"Ｖ","W":"Ｗ","X":"Ｘ","Y":"Ｙ","Z":"Ｚ","1":"１","2":"２","3":"３","4":"４","5":"５","6":"６","7":"７","8":"８","9":"９","0":"０"}
        aesthetics = "".join([(aes_dict[c] if aes_dict.get(c) else c) for c in message])
        yield from ctx.message.delete()
        yield from ctx.send(aesthetics)

    def get_attachment(self, ctx: discord.ext.commands.Context):
        messages = yield from ctx.channel.history(limit=50).flatten()
        for msg in messages:
            if msg.attachments:
                return msg.attachments[0]
        return None

    @commands.command(pass_context=True, aliases=["df", "dfry", "fry"])
    @asyncio.coroutine
    def deepfry(self, ctx):
        """
        Deep fry the most recent image in the channel
        """
        att = yield from self.get_attachment(ctx)
        if att is None:
            yield from ctx.send("Image not found :c")
        else:
            fp = "./db/%s"%(att.filename)
            dest = "./db/%s-deepfried%s"%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                with Image.open(fp) as image:
                    fried = ImageEnhance.Contrast(image).enhance(5.0)
                    fried = ImageEnhance.Color(fried).enhance(2.0)
                    fried.save(dest, quality=20)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except:
                yield from ctx.send("Not an image.")
            os.remove(fp)

    @commands.command(pass_context=True)
    @asyncio.coroutine
    def blur(self, ctx):
        """
        Blur the image
        """
        att = yield from self.get_attachment(ctx)
        if att is None:
            yield from ctx.send("Image not found :c")
        else:
            fp = "./db/%s"%(att.filename)
            dest = "./db/%s-blurred%s"%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                with Image.open(fp) as image:
                    blurred = image.filter(ImageFilter.BoxBlur(radius=3))
                    blurred.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception as e:
                yield from ctx.send("Not an image.")
            os.remove(fp)

def setup(bot):
    bot.add_cog(Fun(bot))
