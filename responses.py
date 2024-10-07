from random import choice, randint


def run_bot():
    load_dotenv
    TOKEN = os.getenv('DISCORD_TOKEN')

def get_response(user_input: str) -> str: 
    lowered: str = user_input.lower()
    
    if lowered == '':
        return 'no response recieved'
    elif 'hello' in lowered:
        return 'hi'
    elif 'roll dice' in lowered:
        return f'you rolled: {randint(1,6)}'

"""
    else:
        return choice(['what',
                        'huh'
                        'i didn\'t understand'])

"""