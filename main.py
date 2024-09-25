import os
from dotenv import load_dotenv
from discord import Intents, Message
from responses import get_response
import asyncio
import yt_dlp
import discord
# step 0: load token from somewhere safe
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)

# step 1: bot setup

intents = Intents.default()
intents.message_content = True #NOQA
bot = discord.Bot(intents=intents)



voice_clients = {}
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
@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running!')


# step 4: handling incoming messages
@bot.event
async def on_message(message: Message) -> None:
    if message.author == bot.user:
        return

    if message.content.startswith("!play"):
        try:
            voice_client = await message.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(e)
        
        try:
            url = message.content.split()[1]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

            voice_clients[message.guild.id].play(player)
        except Exception as e:
            print(e)



    if message.content.startswith("!pause"):
        try:
            voice_clients[message.guild.id].pause()
        except Exception as e:
            print(e)


    if message.content.startswith("!stop"):
        try:
            voice_clients[message.guild.id].stop()
            await voice_clients[message.guild.id].disconnect()
        except Exception as e:
            print(e)


    if message.content.startswith("!resume"):
        try:
            voice_clients[message.guild.id].resume()
        except Exception as e:
            print(e)

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)


# setp 5: main entry point
def main() -> None: 
    bot.run(token=TOKEN)


if __name__ == '__main__':
    main()
