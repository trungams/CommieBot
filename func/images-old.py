#!/usr/bin/python3

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# misc imports
import os, sys, random
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from math import sqrt, pi, sin, cos, tan, atan2
import traceback

halfPi = pi/2
tau = pi*2

class Imaging():
    def __init__(self, bot):
        self.bot = bot


    @asyncio.coroutine
    def __get_attachment(self, ctx: discord.ext.commands.Context):
        messages = yield from ctx.channel.history(limit=50).flatten()
        for msg in messages:
            if msg.attachments:
                return msg.attachments[0]
        return None


    def __motion_blur(self, image: Image, width, height, radius=15):
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
        result = Image.fromarray(output.astype('uint8'))
        return result


    def __motion_filter(self, image, option, radius=15):
        # Options:
        #   0 for horizontal box blur
        #   1 for vertical box blur
        #   2 for circular blur
        #   3 for radial blur
        if option == 0:
            return self.__motion_blur(image, image.width, image.height, radius)
        elif option == 1:
            result = self.__motion_blur(image.transpose(Image.TRANSPOSE), image.height, image.width, radius)
            return result.transpose(Image.TRANSPOSE)
        elif option == 2:
            result = self.__polar_filter(image, 1)
            result = self.__motion_filter(result, 1, radius)
            result = self.__polar_filter(result, 0)
            return result
        elif option == 3:
            result = self.__polar_filter(image, 1)
            result = self.__motion_filter(result, 0, radius)
            result = self.__polar_filter(result, 0)
            return result


    def __polar_filter(self, image, option):
        width   = image.width
        height  = image.height
        centerX = width/2
        centerY = height/2
        radius  = max(centerX, centerY)

        def __polar_transform(x, y):
            theta = t = 0.0
            outx = outy = m = xmax = ymax = 0.0
            r = 0.0

            if option == 0: # rect to polar
                if x >= centerX:
                    if y > centerY:
                        theta = pi - atan2(x-centerX, y-centerY)
                        r = sqrt((x-centerX)**2 + (y-centerY)**2)
                    elif y < centerY:
                        theta = atan2(x-centerX, centerY-y)
                        r = sqrt((x-centerX)**2 + (y-centerY)**2)
                    else:
                        theta = halfPi
                        r = x - centerX
                elif x < centerX:
                    if y < centerY:
                        theta = tau - atan2(centerX-x, centerY-y)
                        r = sqrt((centerX-x)**2 + (centerY-y)**2)
                    elif y > centerY:
                        theta = pi + atan2(centerX-x, y-centerY)
                        r = sqrt((centerX-x)**2 + (y-centerY)**2)
                    else:
                        theta = 1.5 * pi
                        r = centerX - x
                if x != centerX:
                    m = abs(y-centerY) / (x-centerX)
                else:
                    m = 0

                if m <= height/width:
                    if x == centerX:
                        xmax = 0
                        ymax = centerY
                    else:
                        xmax = centerX
                        ymax = m*xmax
                else:
                    ymax = centerY
                    xmax = ymax/m

                outx = (width-1) - (width-1) / tau * theta
                outy = height * r / radius

            elif option == 1: # polar to rect
                theta = x / width * tau
                theta2 = 0.0

                if theta >= 1.5*pi:
                    theta2 = tau - theta
                elif theta >= pi:
                    theta2 = theta - pi
                elif theta >= 0.5*pi:
                    theta2 = pi - theta
                else:
                    theta2 = theta
                t = tan(theta2)
                if t != 0:
                    m = 1 / t
                else:
                    m = 0
                if m <= height/width:
                    if theta2 == 0:
                        xmax = 0
                        ymax = centerY
                    else:
                        xmax = centerX
                        ymax = m * xmax
                else:
                    ymax = centerY
                    xmax = ymax / m

                r = radius * y / height

                nx = -r * sin(theta2)
                ny = r * cos(theta2)

                if theta >= 1.5*pi:
                    outx = centerX - nx
                    outy = centerY - ny
                elif theta >= pi:
                    outx = centerX - nx
                    outy = centerY + ny
                elif theta >= halfPi:
                    outx = centerX + nx
                    outy = centerY + ny
                else:
                    outx = centerX + nx
                    outy = centerY - ny
            return outx, outy

        arr = np.array(image)
        output = np.full(arr.shape, 255)

        outX = outY = srcX = srcY = 0

        for i in range(height):
            for j in range(width):
                srcX, srcY = __polar_transform(outX+i, outY+j)
                y = int(max(0, min(height-1, srcY)))
                x = int(max(0, min(width-1, srcX)))
                output[i][j] = arr[y][x]

        result = Image.fromarray(output.astype('uint8'))
        return result.rotate(270) #if option == 0 else result


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def blur(self, ctx):
        '''
        Blur the image
        '''
        att = yield from self.__get_attachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            fp = './db/%s'%(att.filename)
            dest = './db/%s-blurred%s'%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                yield from ctx.trigger_typing()
                with Image.open(fp) as image:
                    result = image.filter(ImageFilter.GaussianBlur(radius=3))
                    result.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(fp)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def hblur(self, ctx, radius='15'):
        '''
        Motion blur horizontically
        '''
        att = yield from self.__get_attachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            fp = './db/%s'%(att.filename)
            dest = './db/%s-blurred%s'%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                yield from ctx.trigger_typing()
                with Image.open(fp) as image:
                    result = self.__motion_filter(image, 0, int(radius))
                    result.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(fp)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def vblur(self, ctx, radius='15'):
        '''
        Motion blur vertically
        '''
        att = yield from self.__get_attachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            fp = './db/%s'%(att.filename)
            dest = './db/%s-blurred%s'%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                yield from ctx.trigger_typing()
                with Image.open(fp) as image:
                    result = self.__motion_filter(image, 1, int(radius))
                    result.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(fp)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def rblur(self, ctx, radius='15'):
        '''
        Radial blur
        '''
        att = yield from self.__get_attachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            fp = './db/%s'%(att.filename)
            dest = './db/%s-blurred%s'%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                yield from ctx.trigger_typing()
                with Image.open(fp) as image:
                    result = self.__motion_filter(image, 2, int(radius))
                    result.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(fp)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def cblur(self, ctx, radius='15'):
        '''
        Circular blur
        '''
        att = yield from self.__get_attachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            fp = './db/%s'%(att.filename)
            dest = './db/%s-blurred%s'%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                yield from ctx.trigger_typing()
                with Image.open(fp) as image:
                    result = self.__motion_filter(image, 3, int(radius))
                    result.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(fp)


    @commands.command(pass_context=True, aliases=['df', 'dfry', 'fry'])
    @asyncio.coroutine
    def deepfry(self, ctx):
        '''
        Deep fry the most recent image in the channel
        '''
        att = yield from self.__get_attachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            fp = './db/%s'%(att.filename)
            dest = './db/%s-deepfried%s'%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                yield from ctx.trigger_typing()
                with Image.open(fp) as image:
                    result = ImageEnhance.Contrast(image).enhance(1.5)
                    result = ImageEnhance.Sharpness(result).enhance(2.0)
                    result = ImageEnhance.Color(result).enhance(2.0)
                    result.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(fp)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def noise(self, ctx):
        att = yield from self.__get_attachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            fp = './db/%s'%(att.filename)
            dest = './db/%s-deepfried%s'%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                yield from ctx.trigger_typing()
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

                    result = Image.fromarray(noisy_image.astype('uint8'))
                    result.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(fp)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def polar(self, ctx):
        '''
        Transform an image from cartesian to polar coordinates
        '''
        att = yield from self.__get_attachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            fp = './db/%s'%(att.filename)
            dest = './db/%s-blurred%s'%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                yield from ctx.trigger_typing()
                with Image.open(fp) as image:
                    result = self.__polar_filter(image, 0)
                    result.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception:
                #exc_type, exc_value, exc_traceback = sys.exc_info()
                yield from ctx.send('Error occurred.')
                #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            os.remove(fp)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def cart(self, ctx):
        '''
        Transform an image from polar to cartesian coordinates
        '''
        att = yield from self.__get_attachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            fp = './db/%s'%(att.filename)
            dest = './db/%s-blurred%s'%(att.filename[:-4], att.filename[-4:])
            yield from att.save(fp)
            try:
                yield from ctx.trigger_typing()
                with Image.open(fp) as image:
                    result = self.__polar_filter(image, 1)
                    result.save(dest)
                    yield from ctx.message.delete()
                    yield from ctx.send(file=discord.File(fp=dest))
                    os.remove(dest)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(fp)


def setup(bot):
    bot.add_cog(Imaging(bot))
