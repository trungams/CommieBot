#!/usr/bin/python3

# imports for Discord
import discord
from discord.ext import commands
import asyncio

# misc imports
import os, sys, random
import numpy as np
import cv2
import math
import traceback

class Images():
    def __init__(self, bot):
        self.bot = bot


    def __getAttachment(self, ctx: discord.ext.commands.Context):
        messages = yield from ctx.channel.history(limit=100).flatten()
        for msg in messages:
            if msg.attachments:
                return msg.attachments[0]
        return None


    def __polar(self, image):
        height, width = image.shape[:2]
        centerX = width/2
        centerY = height/2
        radius = math.sqrt(width**2 + height**2)/2

        result = cv2.linearPolar(image, (centerX, centerY), radius, cv2.INTER_LINEAR + cv2.WARP_FILL_OUTLIERS)
        return result


    def __cart(self, image):
        height, width = image.shape[:2]
        centerX = width/2
        centerY = height/2
        radius = math.sqrt(width**2 + height**2)/2

        result = cv2.linearPolar(image, (centerX, centerY), radius, cv2.INTER_LINEAR + cv2.WARP_FILL_OUTLIERS + cv2.WARP_INVERSE_MAP)
        return result


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def polar(self, ctx):
        '''
        Transform Cartesian to polar coordinates
        '''
        att = yield from self.__getAttachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            src = './db/%s' % (att.filename)
            dst = './db/%s-polar' % att.filename[:-4] + '.jpg'
            yield from att.save(src)
            try:
                yield from ctx.trigger_typing()
                result = cv2.imread(src, cv2.IMREAD_COLOR)
                result = self.__polar(result)
                cv2.imwrite(dst, result, [cv2.IMWRITE_JPEG_QUALITY, 100])
                yield from ctx.message.delete()
                yield from ctx.send(file=discord.File(fp=dst))
                os.remove(dst)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(src)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def cart(self, ctx):
        '''
        Transform from polar to Cartesian coordinates
        '''
        att = yield from self.__getAttachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            src = './db/%s' % (att.filename)
            dst = './db/%s-cart' % att.filename[:-4] + '.jpg'
            yield from att.save(src)
            try:
                yield from ctx.trigger_typing()
                result = cv2.imread(src, cv2.IMREAD_COLOR)
                result = self.__cart(result)
                cv2.imwrite(dst, result, [cv2.IMWRITE_JPEG_QUALITY, 100])
                yield from ctx.message.delete()
                yield from ctx.send(file=discord.File(fp=dst))
                os.remove(dst)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(src)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def blur(self, ctx, iterations='1'):
        '''
        Blur the image
        '''
        att = yield from self.__getAttachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            src = './db/%s' % (att.filename)
            dst = './db/%s-blur' % att.filename[:-4] + '.jpg'
            yield from att.save(src)
            try:
                yield from ctx.trigger_typing()
                iterations = max(0, min(int(iterations), 100))
                result = cv2.imread(src, cv2.IMREAD_COLOR)
                for i in range(iterations):
                    result = cv2.GaussianBlur(result, (5,5), 0)
                cv2.imwrite(dst, result, [cv2.IMWRITE_JPEG_QUALITY, 100])
                yield from ctx.message.delete()
                yield from ctx.send(file=discord.File(fp=dst))
                os.remove(dst)
            except Exception:
                # exc_type, exc_value, exc_traceback = sys.exc_info()
                yield from ctx.send('Error occurred.')
                # traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            os.remove(src)


    @commands.command(pass_context=True, aliases=['left', 'right'])
    @asyncio.coroutine
    def hblur(self, ctx, radius='10'):
        '''
        Blur the image horizontally
        '''
        att = yield from self.__getAttachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            src = './db/%s' % (att.filename)
            dst = './db/%s-hblur' % att.filename[:-4] + '.jpg'
            yield from att.save(src)
            try:
                yield from ctx.trigger_typing()
                radius = max(1, min(int(radius), 500))
                result = cv2.imread(src, cv2.IMREAD_COLOR)
                result = cv2.blur(result, (radius,1))
                cv2.imwrite(dst, result, [cv2.IMWRITE_JPEG_QUALITY, 100])
                yield from ctx.message.delete()
                yield from ctx.send(file=discord.File(fp=dst))
                os.remove(dst)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(src)


    @commands.command(pass_context=True, aliases=['up', 'down'])
    @asyncio.coroutine
    def vblur(self, ctx, radius='10'):
        '''
        Blur the image vertically
        '''
        att = yield from self.__getAttachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            src = './db/%s' % (att.filename)
            dst = './db/%s-vblur' % att.filename[:-4] + '.jpg'
            yield from att.save(src)
            try:
                yield from ctx.trigger_typing()
                radius = max(1, min(int(radius), 500))
                result = cv2.imread(src, cv2.IMREAD_COLOR)
                result = cv2.blur(result, (1,radius))
                cv2.imwrite(dst, result, [cv2.IMWRITE_JPEG_QUALITY, 100])
                yield from ctx.message.delete()
                yield from ctx.send(file=discord.File(fp=dst))
                os.remove(dst)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(src)


    @commands.command(pass_context=True, aliases=['zoom', 'radial'])
    @asyncio.coroutine
    def rblur(self, ctx, radius='10'):
        '''
        Radial blur
        '''
        att = yield from self.__getAttachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            src = './db/%s' % (att.filename)
            dst = './db/%s-rblur' % att.filename[:-4] + '.jpg'
            yield from att.save(src)
            try:
                yield from ctx.trigger_typing()
                radius = max(1, min(int(radius), 500))
                result = cv2.imread(src, cv2.IMREAD_COLOR)

                result = self.__polar(result)
                result = cv2.blur(result, (radius,1))
                result = self.__cart(result)

                cv2.imwrite(dst, result, [cv2.IMWRITE_JPEG_QUALITY, 100])
                yield from ctx.message.delete()
                yield from ctx.send(file=discord.File(fp=dst))
                os.remove(dst)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(src)


    @commands.command(pass_context=True, aliases=['circle', 'circular', 'spin'])
    @asyncio.coroutine
    def cblur(self, ctx, radius='10'):
        '''
        Circular blur
        '''
        att = yield from self.__getAttachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            src = './db/%s' % (att.filename)
            dst = './db/%s-cblur' % att.filename[:-4] + '.jpg'
            yield from att.save(src)
            try:
                yield from ctx.trigger_typing()
                radius = max(1, min(int(radius), 500))
                result = cv2.imread(src, cv2.IMREAD_COLOR)

                result = self.__polar(result)
                result = cv2.blur(result, (1,radius))
                result = self.__cart(result)

                cv2.imwrite(dst, result, [cv2.IMWRITE_JPEG_QUALITY, 100])
                yield from ctx.message.delete()
                yield from ctx.send(file=discord.File(fp=dst))
                os.remove(dst)
            except Exception:
                yield from ctx.send('Error occurred.')
            os.remove(src)


    @commands.command(pass_context=True, aliases=['df', 'dfry', 'fry'])
    @asyncio.coroutine
    def deepfry(self, ctx, iterations='1'):
        '''
        Deep fry an image, mhmm
        '''
        att = yield from self.__getAttachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            src = './db/%s'%(att.filename)
            dst = './db/%s-fried' % att.filename[:-4] + '.jpg'
            yield from att.save(src)
            try:
                yield from ctx.trigger_typing()
                iterations = max(0, min(int(iterations), 20))
                result = cv2.imread(src, cv2.IMREAD_COLOR)

                kernel = np.array([[0,0,0], [0,1,0], [0,0,0]]) \
                        + np.array([[0,-1,0], [-1,4,-1], [0,-1,0]]) * 0.3
                for i in range(iterations):
                    std = int(np.std(result))
                    # Contrast
                    result = cv2.addWeighted(result, 0.9, result, 0, std*0.3)
                    # Sharpness
                    result = cv2.filter2D(result, 0, kernel)
                    # Saturation
                    result = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
                    result[:,:,1:] = cv2.add(result[:,:,1:], result[:,:,1:])
                    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR)

                cv2.imwrite(dst, result, [cv2.IMWRITE_JPEG_QUALITY, 100])
                yield from ctx.message.delete()
                yield from ctx.send(file=discord.File(fp=dst))
                os.remove(dst)
            except Exception:
                # exc_type, exc_value, exc_traceback = sys.exc_info()
                yield from ctx.send('Error occurred.')
                # traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            os.remove(src)


    @commands.command(pass_context=True)
    @asyncio.coroutine
    def noise(self, ctx, iterations='1'):
        '''
        Add some noise to tha image!!
        '''
        att = yield from self.__getAttachment(ctx)
        if att is None:
            yield from ctx.send('Image not found :c')
        else:
            src = './db/%s'%(att.filename)
            dst = './db/%s-noisy' % att.filename[:-4] + '.jpg'
            yield from att.save(src)
            try:
                yield from ctx.trigger_typing()
                iterations = max(0, min(int(iterations), 20))
                result = cv2.imread(src, cv2.IMREAD_COLOR)

                for i in range(iterations):
                    noise = np.std(result) * np.random.random(result.shape)
                    result = cv2.add(result, noise.astype('uint8'))
                    result = cv2.addWeighted(result, 1, result, 0, -np.std(result)*0.49)

                cv2.imwrite(dst, result, [cv2.IMWRITE_JPEG_QUALITY, 100])
                yield from ctx.message.delete()
                yield from ctx.send(file=discord.File(fp=dst))
                os.remove(dst)
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                yield from ctx.send('Error occurred.')
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            os.remove(src)


def setup(bot):
    bot.add_cog(Images(bot))