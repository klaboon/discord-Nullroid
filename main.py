import os
from dotenv import load_dotenv
#from discord import Intents, Cilent, Message
#from responses import get_response

# step 0: load token from somewhere safe
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)

# step 1: bot setup

intents = intents.default()
intents.message_content = True #NOQA
cilent = Cilent(intents=intents)

# step 2: message functionality
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled possibly)')
        return

        if is_private := user_message[0] == '?':
            user_message = user_message[1:]

        try:
            response: str = get_response(user_message)
            await message.author.send(response) if is_private else message.channel.send(response)
        except Exception as e: # practice logging instead of printing
            print(e)

