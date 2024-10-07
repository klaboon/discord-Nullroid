import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from discord.ext import commands
from responses import get_response
import asyncio
import yt_dlp
import discord
import urllib.parse, urllib.request, re

# step 0: load token from somewhere safe
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# step 1: bot setup

intents = Intents.default()
intents.message_content = True #NOQA
client = commands.Bot(command_prefix="!", intents=intents)

queues = {}
voice_clients = {}
youtube_base_url = 'https://www.youtube.com/'
youtube_results_url = youtube_base_url + 'results?'
youtube_watch_url = youtube_base_url + 'watch?v='
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=3"'}

# step 2: message functionality
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled possibly)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e: # practice logging instead of printing
        print(e)

# step 3: handling startup for bot
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

# step 4: handling incoming messages

async def play_next(ctx):
    if queues[ctx.guild.id] != []:
        link = queues[ctx.guild.id].pop(0)
        await play(ctx, link=link)


@client.command(name="play")
async def play(ctx, *, link):
    try:
        voice_client = await ctx.author.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
    except Exception as e:
        print(e)

    try:

        if youtube_base_url not in link:
            query_string = urllib.parse.urlencode({
                'search_query': link
            })

            content = urllib.request.urlopen(
                youtube_results_url + query_string
            )

            search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())

            link = youtube_watch_url + search_results[0]
        
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))

        song = data['url']
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

        voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        await ctx.send(f'Now playing {l}.')
    except Exception as e:
        print(e)

    @client.command("clear_queue")
    async def clear_queue(ctx):
        if ctx.guild.id in queues:
            queues[ctx.guild.id].clear()
            await ctx.send("Queue cleared.")
        else:
            await ctx.send("There is no queue to clear.")

    @client.command(name="pause")
    async def pause(ctx):
        try:
            voice_clients[ctx.guild.id].pause()
            await ctx.send("Paused.")
        except Exception as e:
            print(e)

    @client.command(name="stop")
    async def stop(ctx):
        try:
            voice_clients[ctx.guild.id].stop()
            await voice_clients[ctx.guild.id].disconnect()
            del voice_clients[ctx.guild.id]
            await ctx.send("Disconnected.")
        except Exception as e:
            print(e)

    @client.command(name="resume")
    async def resume(ctx):
        try:
            voice_clients[ctx.guild.id].resume()
            await ctx.send("Resumed.")
        except Exception as e:
            print(e)

    @client.command(name="queue")
    async def queue(ctx, *, url):
        if ctx.guild.id not in queues:
            queues[ctx.guild.id] = []
        queues[ctx.guild.id].append(url)
        await ctx.send("Added to queue.")

    @client.command(name="skip")
    async def skip(ctx):
        try:
            await ctx.send("Skipped currently playing.")
            voice_clients[ctx.guild.id].stop()
            await play_next(ctx)
        except Exception as e:
            print(e)

# setp 5: main entry point
def main() -> None: 
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()
