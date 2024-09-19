import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response

# step 0: load token from somewhere safe
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)

# step 1: bot setup

intents = Intents.default()
intents.message_content = True #NOQA
client = Client(intents=intents)

voice_cilents = {}
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg = {'options': '-vn'}

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
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    if message.content.startswith("?play"):
        try:
            voice_cilent = await message.author.voice.channel.connect()
            voice_cilents[voice_cilent.guild.id] = voice_cilent
        except Exception as e:
            print(e)
        
        try:
            url = message.content.split()[1]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.ffmpegPCMAudio(song, **ffmpeg_options)

            voice_cilents[message.guild.id].play(player)
        except Exception as e:
            print(e)
            

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')
    await send_message(message, user_message)


# setp 5: main entry point
def main() -> None: 
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()
