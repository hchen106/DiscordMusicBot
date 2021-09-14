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
    await ctx.send('pong')

bot.run('ODg3NDMzMDM2MTgwODg5NjMx.YUEEaw.Ut67XONSAnuYAMbP9fzFKpCTRdY')