from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Cilent, Message
from responses import get_response

# step 0: load token from somewhere safe
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)