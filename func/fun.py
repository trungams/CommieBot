#!/usr/bin/python3


# imports for Discord
import discord
from discord.ext import commands
import asyncio


# misc imports
import os, random, math
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np


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
        aes_dict = {" ":"　","a":"ａ","b":"ｂ","c":"ｃ","d":"ｄ","e":"ｅ","f":"ｆ","g":"ｇ","h":"ｈ","i":"ｉ","j":"ｊ","k":"ｋ","l":"ｌ","m":"ｍ",
					"n":"ｎ","o":"ｏ","p":"ｐ","q":"ｑ","r":"ｒ","s":"ｓ","t":"ｔ","u":"ｕ","v":"ｖ","w":"ｗ","x":"ｘ","y":"ｙ","z":"ｚ",
					"A":"Ａ","B":"Ｂ","C":"Ｃ","D":"Ｄ","E":"Ｅ","F":"Ｆ","G":"Ｇ","H":"Ｈ","I":"Ｉ","J":"Ｊ","K":"Ｋ","L":"Ｌ","M":"Ｍ",
					"N":"Ｎ","O":"Ｏ","P":"Ｐ","Q":"Ｑ","R":"Ｒ","S":"Ｓ","T":"Ｔ","U":"Ｕ","V":"Ｖ","W":"Ｗ","X":"Ｘ","Y":"Ｙ","Z":"Ｚ",
					"1":"１","2":"２","3":"３","4":"４","5":"５","6":"６","7":"７","8":"８","9":"９","0":"０"}
        aesthetics = "".join([(aes_dict[c] if aes_dict.get(c) else c) for c in message])
        yield from ctx.message.delete()
        yield from ctx.send(aesthetics)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def thicc(self, ctx, *, message):
        """
        乇乂丅尺卂 丅卄工匚匚
        """
        thicc_dict = {"a":"卂","b":"乃","c":"匚","d":"刀","e":"乇","f":"下","g":"厶","h":"卄",
						"i":"工","j":"丁","k":"长","l":"乚","m":"从","n":"𠘨","o":"口","p":"尸",
						"q":"㔿","r":"尺","s":"丂","t":"丅","u":"凵","v":"リ","w":"山","x":"乂","y":"丫","z":"乙"}
        extra_thicc = "".join([(thicc_dict[c] if thicc_dict.get(c) else c) for c in message.lower()])
        yield from ctx.message.delete()
        yield from ctx.send(extra_thicc)


    def get_attachment(self, ctx: discord.ext.commands.Context):
        messages = yield from ctx.channel.history(limit=50).flatten()
        for msg in messages:
            if msg.attachments:
                return msg.attachments[0]
        return None


    def motion_blur(self, image: Image, width, height, radius):
        arr = np.array(image)
        output = np.copy(arr)
        size = 2*radius+1

        for y in range(height):
            if(arr.shape == 2): # B/W image
                for i in range(-radius, radius+1):
                    pixel = arr[y][min(width-1, max(i, 0))]

                for x in range(width):
                    output[y][x] = pixel/size

                    pixel1 = arr[y][min(x+radius+1, width-1)]
                    pixel2 = arr[y][max(x-radius, 0)]

                    pixel += pixel1 - pixel2
            else: # RGB image
                r = g = b = 0
                for i in range(-radius, radius+1):
                    pixel = arr[y][min(width-1, max(i, 0))]
                    r += int(pixel[0])
                    g += int(pixel[1])
                    b += int(pixel[2])  # Red, Green, Blue values

                for x in range(width):
                    output[y][x][0] = r/size
                    output[y][x][1] = g/size
                    output[y][x][2] = b/size

                    pixel1 = arr[y][min(x+radius+1, width-1)]
                    pixel2 = arr[y][max(x-radius, 0)]

                    r += int(pixel1[0]) - int(pixel2[0])
                    g += int(pixel1[1]) - int(pixel2[1])
                    b += int(pixel1[2]) - int(pixel2[2])
        blurred = Image.fromarray(output.astype('uint8'))
        return blurred


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
                yield from ctx.send("Error occurred.")
            os.remove(fp)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def hblur(self, ctx):
        """
        Motion blur horizontically
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
                    blurred = self.motion_blur(image, image.width, image.height, 15)
                    blurred.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception as e:
                yield from ctx.send("Error occurred.")
            os.remove(fp)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def vblur(self, ctx):
        """
        Motion blur vertically
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
                    image = image.transpose(Image.TRANSPOSE)
                    blurred = self.motion_blur(image, image.width, image.height, 15)
                    blurred = blurred.transpose(Image.TRANSPOSE)
                    blurred.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception as e:
                yield from ctx.send("Error occurred.")
            os.remove(fp)


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
                    fried = ImageEnhance.Contrast(image).enhance(1.5)
                    fried = ImageEnhance.Sharpness(fried).enhance(2.0)
                    fried = ImageEnhance.Color(fried).enhance(2.0)
                    fried.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception:
                yield from ctx.send("Error occurred.")
            os.remove(fp)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def noise(self, ctx):
        att = yield from self.get_attachment(ctx)
        if att is None:
            yield from ctx.send("Image not found :c")
        else:
            fp = "./db/%s"%(att.filename)
            dest = "./db/%s-deepfried%s"%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                with Image.open(fp) as image:
                    img_arr = np.array(image)

                    width = img_arr.shape[1]
                    height = img_arr.shape[0]

                    noise = 12 * np.random.randn(height, width)
                    noisy_image = np.copy(img_arr)
                    if len(img_arr.shape) == 2: # B/W image
                        noisy_image = img_arr + noise
                    else: # RGB image
                        noisy_image[:,:,0] = img_arr[:,:,0] + noise
                        noisy_image[:,:,1] = img_arr[:,:,1] + noise
                        noisy_image[:,:,2] = img_arr[:,:,2] + noise

                    noisy = Image.fromarray(noisy_image.astype('uint8'))
                    noisy.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception:
                yield from ctx.send("Error occurred.")
            os.remove(fp)


def setup(bot):
    bot.add_cog(Fun(bot))
