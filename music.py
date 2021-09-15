import discord
from discord import voice_client
from discord.ext import commands
import youtube_dl
import pafy

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []
    
    async def check_queue(self, ctx):
        if len(self.queue) > 0:
            #ctx.voice_client.stop()
            await self.play_song(ctx, self.queue[0])
            self.queue.pop(0); 


    async def search_song(self, amount, song, get_url=False):
        info = youtube_dl.YoutubeDL({"format" : "bestaudio", "quiet" : True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch")
        if len(info["entries"]) == 0: return None

        return [entry["webpage_url"] for entry in info["entries"]] if get_url else info
    
    async def play_song(self, ctx, url):
 
        
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format': 'bestaudio'}
        vc = ctx.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            vc.play(source, after=lambda error: self.client.loop.create_task(self.check_queue(ctx)))
        #song = pafy.new(url).getbestaudio().url
        #ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song)), after=lambda error: self.client.loop.create_task(self.check_queue(ctx)))
    
    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send('please join the chat')
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def disconnect(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command()
    async def play(self, ctx, *, song=None):
        if song is None: 
            await ctx.send("You forgot to include a song to search for.") 
            return

        url = song
        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            song_info = await self.search_song(1, song)

            embed = discord.Embed(title=f"Results for '{song}':", description="*You can use these URL's to play an exact song if the one you want isn't the first result.*\n", colour=discord.Colour.red())
        
            amount = 0
            for entry in song_info["entries"]:
            
                url = f"{entry['webpage_url']}"
                embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
                amount += 1

            await ctx.send(embed=embed)
        
        if ctx.voice_client.source is not None:
            size = len(self.queue)
            self.queue.append(url)
            await ctx.send(text=f"added to the queue {size}")
        
        await self.play_song(ctx, url)
        
    @commands.command()
    async def skip(self, ctx):
        await ctx.voice_client.stop()
        self.queue.pop(0)
        if len(self.queue) > 0:
            self.play_song(ctx, self.queue[0])
        else:
            await ctx.voice_client.stop()
        
    
    @commands.command()
    async def pause(self, ctx):
        await ctx.voice_client.pause()
        await ctx.send('pause')

    @commands.command()
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        await ctx.send('resume')        

        

def setup(client):
    client.add_cog(music(client))