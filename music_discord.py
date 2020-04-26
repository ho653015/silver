import asyncio
import functools
import itertools
import math
import random
import datetime
import sys
import discord
import youtube_dl
from async_timeout import timeout
client = discord.Client()
youtube_dl.utils.bug_reports_message = lambda: ''
musics = {}
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}
ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, msg: discord.message, source, *, data, volume=0.5):
        super().__init__(source, volume)
        print(source)
        self.requester = msg.author
        self.data = data
        self.thumbnail = data.get('thumbnail')
        self.duration = datetime.timedelta(seconds=int(data.get('duration')))
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, msg: discord.message, url, *, loop=None, stream=False):

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(msg, discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)


@client.event
async def on_ready():
    bid = (str(client.user.id))
    print("봇 이름 : " + bid)
    bname = client.user.name
    print("봇이름 : " + bname)
    print("START")


def create_embed(player):
    embed = (discord.Embed(title='현재곡',
                           description=f'{player.title}',
                           color=0x43b581)
             .add_field(name='길이', value=player.duration)
             .add_field(name='신청자', value=player.requester)
             .set_thumbnail(url=player.thumbnail))

    return embed

def add_embed(player):
    embed = (discord.Embed(title='추가됨',
                           description=f'{player.title}',
                           color=0x43b581)
             .add_field(name='길이', value=player.duration)
             .add_field(name='신청자', value=player.requester)
             .set_thumbnail(url=player.thumbnail))

    return embed
async def check(voice, message):
    while True:
        if voice.is_playing() == False:
            if next_music(voice, message) is None:
                del musics[message.author.guild.id]
                return
        await asyncio.sleep(7)


def next_music(voice, message):
    mchekc = musics[message.author.guild.id]
    if mchekc != []:
        rmusic = musics[message.author.guild.id].pop(0)
        voice.play(rmusic)
    return 1


@client.event
async def on_message(message):
    if message.content.startswith("/play") or message.content.startswith("/p"):
        voice_client = message.author.voice.channel
        try:
            url = str(message.content).split("/play ")[1]
        except:
            pass
        try:
            url = str(message.content).split("/p ")[1]
        except:
            pass
        player = await YTDLSource.from_url(message, url, stream=True)
        serverid = message.author.guild.id
        try:
            voice = await voice_client.connect()
            musics[serverid] = [player]
            await message.channel.send(embed=create_embed(player))
            next_music(voice, message)
            client.loop.create_task(check(voice, message))
        except:
            voice = message.author.guild.voice_client
            musics[serverid].append(player)
            await message.channel.send(f"대기열 : {player.title}")
            await message.channel.send(embed=add_embed(player))


    if message.content.startswith("/stop"):
        voice_client = message.author.guild.voice_client
        await voice_client.disconnect()
        del musics[message.author.guild.id]

    if message.content.startswith("/skip") or message.content.startswith("/s"):
        voice = message.author.guild.voice_client
        try:
            await message.channel.send(f"{voice.source.title}를 스킵했단다 ^^")
        except AttributeError:
            await message.channel.send("예 스킵 가능한 곡이없단다!")
            return
        voice.stop()


    if message.content.startswith("/queue"):
        text = ""
        for index,i in enumerate(musics[message.author.guild.id]):
            text = text + f"`{index+1}. {i.title} - {i.requester}`\n"
            if index == 4:
                break
        embed = discord.Embed(title="대기열", description=text, color=0x43b581)
        if len(musics[message.author.guild.id])-5 >= 0:
            embed.set_footer(text=f"+ {len(musics[message.author.guild.id]) - 5}개 대기중...")
        else :
            embed.set_footer(text=f"+ 0개 대기중...")
        await message.channel.send(embed=embed)

    if message.content.startswith(".test"):
        voice = message.author.guild.voice_client
        next_music(voice, message)


client.run('NTAzMDM1MDA3NzQ5ODQ5MTEz.XqVhXA.pJyoifqcXsDfPN0QZUk6doQpHB0')


