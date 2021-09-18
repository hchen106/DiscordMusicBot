import discord
from discord.ext import commands
import youtube_dl
import music

cogs = [music]


bot = commands.Bot(command_prefix = '!')

for i in range(len(cogs)) :
    cogs[i].setup(bot)

@bot.command()
async def ping(ctx):
    
    embed = discord.Embed(title="Song100", description="This is my song", colour=discord.Colour.dark_blue())
    await ctx.send('pong')
    await ctx.send(embed=embed)


bot.run('')