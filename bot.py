# bot.py
import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
user_states = {}

def get_response(message, user_id):
    p_message = message.lower()

    if p_message == 'hello':
        return 'Hey there'
    if '/setup' in p_message:
        user_states[user_id] = {'step': 0, 'answers': []}
        return "Share some basic information like your age, sex, location, etc"
    if '/preference' in p_message:
        user_states[user_id] = {'step': 0, 'answers': []}
        return "What type of relationship are you looking for? Whether it's a meaningful connection, casual dating, or something else entirely, let us know!"    
    if '/match' in p_message:
        return "Here are few folks I think you would hit it off with"
    if '/like' in p_message:
        discord_user = p_message[5:].replace(" ","")
        return f"Starting a private server with {discord_user}"
    if user_id in user_states:
        user_state = user_states[user_id]
        step = user_state['step']

        if step == 0:
            # handle answers for setup and preference here
            user_state['answers'].append(message)
            del user_states[user_id]
            return 'Thank sharing that'

    return 'I am not sure how to respond to that.'

async def send_message(message, user_message, is_private):
    try:
        response = get_response(user_message, message.author.id)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f'{username} said: "{user_message}" ({channel})')

        if user_message.startswith('?'):
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)

    client.run(TOKEN)