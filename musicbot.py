import discord
from discord.ext import commands
import youtube_dl
import pafy
import constants


class MusicBot(commands.Cog):
    # MARK: Setup functions
    def __init__(self, client):
        self.client = client
        self.song_queue = {}

        self.setup()
    
    def setup(self):
        for guild in self.client.guilds:
            self.song_queue[guild.id] = []

    # MARK: Helper functions 
    async def check_queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) > 0:
            ctx.voice_client.stop()
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)

    async def search_song(self, amount, song_name, get_url=False):
        data = await self.client.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL(constants.YDL_OPTIONS).extract_info(f"ytsearch{amount}:{song_name}", download=False, ie_key="YoutubeSearch"))
        if len(data["entries"]) == 0:
            return None

        return ([entry["webpage_url"] for entry in data["entries"]] if get_url else data)
    
    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url)), after=lambda error: self.client.loop.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5

    # MARK: Discord commands methods
    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send(constants.JOIN_NOT_IN_VOICE_CHAT)
        
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
        await ctx.author.voice.channel.connect()
    
    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()

        await ctx.send(constants.LEAVE_NOT_IN_VOICE_CHAT)

    @commands.command()
    async def play(self, ctx, *, song=None):
        if song is None:
            return await ctx.send(constants.PLAY_SONG_NOT_INCLUDED)
        if ctx.author.voice is None:
            return await ctx.send(constants.JOIN_NOT_IN_VOICE_CHAT)
        if ctx.voice_client is None:
            await self.join(ctx)
        
        # Song is not a url
        if not (constants.YOUTUBE_URL_1 in song or constants.YOUTUBE_URL_2 in song):
            await ctx.send(constants.SEARCH_SONG)

            result = await self.search_song(constants.DEFAULT_AMOUNT_OF_SONGS, song, get_url=True)
            if result is None:
                return await ctx.send(constants.SONG_NOT_FOUND)
            song = result[0]
        
        if ctx.voice_client.source is not None and ctx.voice_client.is_playing():
            queue_len = len(self.song_queue[ctx.guild.id])
            if queue_len < 10:
                self.song_queue[ctx.guild.id].append(song)
                return await ctx.send(constants.ADDED_TO_QUEUE)
            else:
                return await ctx.send(constants.QUEUE_LIMIT)
        
        await self.play_song(ctx, song)
        await ctx.send(f"Now playing: {song}")

    @commands.command()
    async def search(self, ctx, *, song_name=None):
        if song_name is None: 
            return await ctx.send(constants.SEARCH_SONG_NOT_INCLUDED)

        await ctx.send(constants.SEARCH_SONG)
        data = await self.search_song(constants.DEFAULT_AMOUNT_OF_SONGS_TO_SEARCH, song_name)
        embed = discord.Embed(title=f"Results for '{song_name}': ", description=constants.SEARCH_DESCRIPTION, colour=discord.Colour.red())  
        amount = 0
        for entry in data["entries"]:
            embed.description += f"[{entry.get('title')}]({entry.get('webpage_url')})\n"
            amount += 1
        
        embed.set_footer(text=f"Displaying the first {amount} results.")
        await ctx.send(embed=embed)

    @commands.command()
    async def queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send(constants.QUEUE_EMPTY)
        
        embed = discord.Embed(title="Song Queue", description="", colour=discord.Colour.dark_gold())
        index = 1
        for url in self.song_queue[ctx.guild.id]:
            embed.description += f"{index}. {url}\n"
            index += 1
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send(constants.SKIP_NO_SONG)
        if ctx.author.voice is None:
            return await ctx.send(constants.SKIP_AUTHOR_NOT_CONNECTED)
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send(constants.SKIP_AUTHOR_IN_DIFFERENT_CHANNEL)

        await ctx.send(constants.SKIPPED)
        
        ctx.voice_client.stop()
        await self.check_queue(ctx)

    @commands.command()
    async def pause(self, ctx):
        ctx.voice_client.pause()
        await ctx.send(constants.PAUSED)
    
    @commands.command()
    async def resume(self, ctx):
        ctx.voice_client.resume()
        await ctx.send(constants.RESUMED)