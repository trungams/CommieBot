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
    def mock(self, ctx, *, msg: str=None):
        """
        mOcKinG sPoNGeBOb
        """
        words = msg.split()
        mix = "".join([(c.upper() if random.randint(0, 1) else c.lower()) for c in msg])
        yield from ctx.send(mix)
        yield from ctx.message.delete()

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
    @commands.is_owner()
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
