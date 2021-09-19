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
            url, name = self.song_queue[ctx.guild.id][0]
            await self.play_song(ctx, url)
            self.song_queue[ctx.guild.id].pop(0)

            embed = discord.Embed(
                title=f"Now playing: {name}", description=f"Link: [{name}]({url})", colour=discord.Colour.green())
            await ctx.send(embed=embed)

    async def search_song(self, amount, song_name, get_url=False):
        data = await self.client.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL(constants.YDL_OPTIONS).extract_info(f"ytsearch{amount}:{song_name}", download=False, ie_key="YoutubeSearch"))
        if len(data["entries"]) == 0:
            return None

        return ([(entry.get("webpage_url"), entry.get("title")) for entry in data["entries"]] if get_url else data)

    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
            url)), after=lambda error: self.client.loop.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5

    # MARK: Discord commands methods
    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(
                title=constants.JOIN_NOT_IN_VOICE_CHAT, description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)

        if ctx.voice_client is not None:
            if ctx.author.voice.channel.id == ctx.voice_client.channel.id:
                embed = discord.Embed(
                    title=constants.JOIN_ALREADY_IN_VOICE_CHAT, description="", colour=discord.Colour.red())
                return await ctx.send(embed=embed)
            await ctx.voice_client.disconnect()
        await ctx.author.voice.channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()

        embed = discord.Embed(title=constants.LEAVE_NOT_IN_VOICE_CHAT,
                              description="", colour=discord.Colour.red())
        await ctx.send(embed=embed)

    @commands.command()
    async def play(self, ctx, *, song=None):
        if song is None:
            if ctx.voice_client is not None and ctx.voice_client.source is not None and not ctx.voice_client.is_playing():
                return await self.resume(ctx)

            embed = discord.Embed(
                title=constants.PLAY_SONG_NOT_INCLUDED, description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)
        if ctx.author.voice is None:
            embed = discord.Embed(
                title=constants.JOIN_NOT_IN_VOICE_CHAT, description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)
        if ctx.voice_client is None:
            await self.join(ctx)

        # Song is not a url
        if not (constants.YOUTUBE_URL_1 in song or constants.YOUTUBE_URL_2 in song):
            await ctx.send(constants.SEARCH_SONG)

            result = await self.search_song(constants.DEFAULT_AMOUNT_OF_SONGS, song, get_url=True)
            if result is None:
                embed = discord.Embed(title=constants.SONG_NOT_FOUND_TITLE,
                                      description=constants.SONG_NOT_FOUND_DESCRIPTION, colour=discord.Colour.red())
                return await ctx.send(embed=embed)
            song, song_name = result[0]

        if ctx.voice_client.source is not None and ctx.voice_client.is_playing():
            queue_len = len(self.song_queue[ctx.guild.id])
            if queue_len < 10:
                self.song_queue[ctx.guild.id].append((song, song_name))
            embed = discord.Embed(title=(constants.ADDED_TO_QUEUE if queue_len <
                                  10 else constants.QUEUE_LIMIT), description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title=f"Now playing: {song_name}", description=f"Link: [{song_name}]({song})", colour=discord.Colour.green())
        await ctx.send(embed=embed)
        await self.play_song(ctx, song)

    @commands.command()
    async def search(self, ctx, *, song_name=None):
        if song_name is None:
            return await ctx.send(constants.SEARCH_SONG_NOT_INCLUDED)

        await ctx.send(constants.SEARCH_SONG)
        data = await self.search_song(constants.DEFAULT_AMOUNT_OF_SONGS_TO_SEARCH, song_name)
        embed = discord.Embed(
            title=f"Results for '{song_name}': ", description=constants.SEARCH_DESCRIPTION, colour=discord.Colour.red())
        amount = 0
        for entry in data["entries"]:
            embed.description += f"[{entry.get('title')}]({entry.get('webpage_url')})\n"
            amount += 1

        embed.set_footer(text=f"Displaying the first {amount} results.")
        await ctx.send(embed=embed)

    @commands.command()
    async def queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) == 0:
            embed = discord.Embed(
                title=constants.QUEUE_EMPTY, description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="Song Queue", description="", colour=discord.Colour.dark_gold())
        index = 1
        for url, name in self.song_queue[ctx.guild.id]:
            embed.description += f"{index}. [{name}]({url})\n"
            index += 1

        await ctx.send(embed=embed)

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client is None:
            embed = discord.Embed(
                title=constants.SKIP_NO_SONG, description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)
        if ctx.author.voice is None:
            embed = discord.Embed(title=constants.SKIP_AUTHOR_NOT_CONNECTED,
                                  description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            embed = discord.Embed(title=constants.SKIP_AUTHOR_IN_DIFFERENT_CHANNEL,
                                  description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)

        embed = discord.Embed(title=constants.SKIPPED,
                              description="", colour=discord.Colour.green())
        await ctx.send(embed=embed)

        ctx.voice_client.stop()
        await self.check_queue(ctx)

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client is None:
            embed = discord.Embed(
                title=constants.SKIP_NO_SONG, description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)
        if ctx.author.voice is None:
            embed = discord.Embed(title=constants.SKIP_AUTHOR_NOT_CONNECTED,
                                  description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            embed = discord.Embed(title=constants.SKIP_AUTHOR_IN_DIFFERENT_CHANNEL,
                                  description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)
        if ctx.voice_client.source is not None and not ctx.voice_client.is_playing():
            embed = discord.Embed(
                title=constants.PAUSED_ALREADY, description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)

        ctx.voice_client.pause()
        embed = discord.Embed(title=constants.PAUSED,
                              description="", colour=discord.Colour.green())
        await ctx.send(embed=embed)

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client is None:
            embed = discord.Embed(
                title=constants.SKIP_NO_SONG, description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)
        if ctx.author.voice is None:
            embed = discord.Embed(title=constants.SKIP_AUTHOR_NOT_CONNECTED,
                                  description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            embed = discord.Embed(title=constants.SKIP_AUTHOR_IN_DIFFERENT_CHANNEL,
                                  description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)
        if ctx.voice_client.source is not None and ctx.voice_client.is_playing():
            embed = discord.Embed(
                title=constants.RESUMED_ALREADY, description="", colour=discord.Colour.red())
            return await ctx.send(embed=embed)

        ctx.voice_client.resume()
        embed = discord.Embed(title=constants.RESUMED,
                              description="", colour=discord.Colour.green())
        await ctx.send(embed=embed)
