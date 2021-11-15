import discord
from discord import voice_client
from discord.ext import commands
import youtube_dl
import pafy
import json


class music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []
    
    async def check_queue(self, ctx):
        size = len(self.queue)
        if size >= 0:
            ctx.voice_client.stop()
            if size > 0:
                await self.play_song(ctx, self.queue[0])
                self.queue.pop(0)


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
            song_title = info.get('title', None)
            embed = discord.Embed(title = f"Now Playing▶️   {song_title}", description="", colour=discord.Colour.red())
            await ctx.send(embed=embed)  
      
        #song = pafy.new(url).getbestaudio().url
        #ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song)), after=lambda error: self.client.loop.create_task(self.check_queue(ctx)))
    
    async def getUrlInfo(self, url):
        YDL_OPTIONS = {'format': 'bestaudio'}
        ydl =  youtube_dl.YoutubeDL(YDL_OPTIONS)
        return ydl.extract_info(url, download=False)


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
    async def talk(self, ctx):
        
        song = 'lalisa'
        await ctx.send(f'!play {song}')
        song_info = await self.search_song(1, song)  
        embed = discord.Embed(title=f"Results for '{song}':", description="", colour=discord.Colour.red())
        
        amount = 0
        for entry in song_info["entries"]:   
            url = f"{entry['webpage_url']}"
            embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
            amount += 1

        await self.play_song(ctx, url)



    @commands.command()
    async def play(self, ctx, *, song=None):
        if song is None: 
            await ctx.send("You forgot to include a song to search for.") 
            return

        url = song
        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            song_info = await self.search_song(1, song)

            embed = discord.Embed(title=f"Results for '{song}':", description="", colour=discord.Colour.red())
        
            amount = 0
            for entry in song_info["entries"]:
            
                url = f"{entry['webpage_url']}"
                embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
                amount += 1

            await ctx.send(embed=embed)
        
        if ctx.voice_client.source is not None:
            size = len(self.queue)
            self.queue.append(url)
            return await ctx.send(f"added to the queue position: {size + 1}.")
        
        await self.play_song(ctx, url)
        
    @commands.command()
    async def skip(self, ctx):
        ctx.voice_client.stop()
        await self.check_queue(ctx)
        await ctx.send("Skipped!")
   
    @commands.command()
    async def pause(self, ctx):
        ctx.voice_client.pause()
        await ctx.send('paused  ⏸️')

    @commands.command()
    async def resume(self, ctx):
        ctx.voice_client.resume()
        await ctx.send('resumed  ⏯️')        

    @commands.command()
    async def queue(self, ctx):
        if len(self.queue) == 0:
            return await ctx.send("There is no song in the queue")
        
        embed = discord.Embed(title="Queue List", description="", colour=discord.Colour.blue())
        i = 1
        for info in self.queue:
            YDL_OPTIONS = {'format': 'bestaudio'}
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info_dict = ydl.extract_info(info, download=False)
                video_title = info_dict.get('title', None)
            
            embed.description += f"{i}). {video_title}\n"
            i += 1
        await ctx.send(embed = embed)

    @commands.command()
    async def jsontestw(self, ctx):
        newdict = {"name": "new song", "url": "www.123.com"}
        newlist = []
        with open('playlist.json', "r+") as f:
            f_data = f.read()
            data = json.loads(f_data)
            print(data['list'][4])
            f.close()
        
    @commands.command()
    async def createlist(self, ctx, listname=None):
         if listname is None:
             await ctx.send("Please Enter a list name")
             return
         with open('playlist.json', "r+") as f:
            f_data = f.read()
            data = json.loads(f_data)
            if listname in data:
                await ctx.send("List Name already exist, please Enter a new List name")
                return
            data[listname] = []
            f.seek(0)
            json.dump(data, f, indent=4)
            f.close()
         await ctx.send( listname +" play list is CREATED")

    @commands.command()
    async def addsong(self, ctx, listname, songname=None):
         if listname is None:
            await ctx.send("Please Enter a list name")
            return
         with open('playlist.json', "r+") as f:  
            f_data = f.read()
            data = json.loads(f_data)
            if listname not in data :
                await ctx.send('No such list')
                return
            
            if songname is None:
                await ctx.send('Please enter song name')
                return
            name = ''
            url = songname
            if not ("youtube.com/watch?" in songname or "https://youtu.be/" in songname):
                 info = await self.search_song(1, songname)
                 for entry in info["entries"]:
                    url = f"{entry['webpage_url']}"
                    name = f"{entry['title']}"
            else:
                info = await self.getUrlInfo(url)
                name = info.get('title', None) 
            
            newsong = {"name" : name, "url": url}
            data[listname].append(newsong)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.close()
         await ctx.send("new song is ADDED to " + listname + " play list")

    @commands.command()
    async def playlist(self, ctx, songlist=None):
        self.queue.clear()
        songs = []
        if songlist is None:
             await ctx.send("Please Enter a list name")
             return
        with open('playlist.json', "r+") as f:
            f_data = f.read()
            data = json.loads(f_data)
            if songlist not in data:
                await ctx.send('No such list')
                return
            songs = data[songlist]
            f.close()
        for song in songs:
            self.queue.append(song['url'])
        if(not self.queue):
            await ctx.send('There are no song in the list')
            return
        firstsong = self.queue.pop(0)
        await self.play_song(ctx, firstsong)
    
    @commands.command()
    async def viewlist(self, ctx, songlist=None):
        if songlist is None:
            await ctx.send("Please Enter a list name")
            return
        names = []
        with open('playlist.json', "r+") as f:
            f_data = f.read()
            data = json.loads(f_data)
            if songlist not in data:
                await ctx.send('No such list')
                return
            names = data[songlist]
            f.close()
        embed = discord.Embed(title=songlist, description="", colour=discord.Colour.blue())
        i = 1
        for song in names:
            songname = song['name']
            embed.description += f"{i}). {songname}\n"
            i += 1
        await ctx.send(embed = embed)
      
def setup(client):
    client.add_cog(music(client))