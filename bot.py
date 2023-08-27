# bot.py
import os
import discord
import pymongo
import random
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

mongodb_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=3_600_000)

# Create dataset and collection
db = mongodb_client.cupidgpt
collection = db.profiles
user_states = {}
sex = ""
preference_male = ["Here is someone interesting for you: Mia - The Social Butterfly: Mia lights up any room she enters with her infectious energy and vibrant personality. Her social calendar is filled with art gallery openings, live music concerts, and cozy gatherings with friends. As a fashion enthusiast, she believes that every day is an opportunity to express herself through style. Mia is drawn to individuals who embrace life with enthusiasm and are ready to dance through the rhythms of fun, laughter, and shared experiences.",
                  "Here is someone interesting for you: Sophia - The Intellectual Dreamer: Meet Sophia, an intellectual soul with a penchant for the profound. Lost in the pages of literature and captivated by philosophical ponderings, she embraces the world of ideas with an open heart. When she's not immersed in thought, she enjoys strolling through art galleries, where each stroke of the brush tells a unique story. Sophia seeks a partner who can match her depth of conversation and is equally curious about life's mysteries. Engaging in debates over coffee or cozying up to timeless films are among her favorite pastimes.",
                  "Here is someone interesting for you:Nina - The Nature Lover: Nature is where Nina truly feels alive. Her weekends are spent chasing sunsets on hiking trails, kayaking through tranquil waters, and sharing moments of wonder with furry companions on pet-friendly adventures. A lover of simplicity, she finds beauty in the little things, like the rustling of leaves and the sound of rain on a rooftop. Nina desires a partner who shares her passion for the great outdoors and is ready to embark on unforgettable journeys into the heart of nature."  ]
preference_female = ["Here is someone interesting for you: Ethan - The Adventure Seeker: Ethan is a thrill-seeker who lives for adrenaline-pumping experiences. Whether he's conquering steep mountain trails, diving into ocean depths, or embarking on spontaneous road trips, he's always up for an adventure. When he's not exploring the great outdoors, Ethan enjoys tinkering with mechanics and fixing things. He's looking for a partner who shares his passion for exploration and isn't afraid to dive headfirst into life's daring",
                    "Here is someone interesting for you: Lucas - The Intellectual Conversationalist: Lucas is a man of intellect and depth, with a fascination for unraveling the mysteries of the world. A voracious reader and a lover of philosophical discussions, he finds meaning in the exchange of ideas. Lucas delights in spending evenings under starry skies, lost in conversations that traverse various realms of thought. He's seeking a partner who can engage him in stimulating discussions and explore the boundless horizons of the mind together.",
                    "Here is someone interesting for you:Leo - The Music Maestro: Leo's world revolves around music. He's a gifted musician who's equally at home strumming a guitar or spinning tunes on the turntable. The stage is his canvas, and he loves to bring people together through the universal language of melody. When he's not performing, Leo enjoys quiet moments at home, savoring the notes of his vinyl collection or experimenting with new recipes. He's hoping to find a partner who can harmonize with his passion for music and share moments that resonate with the rhythm of life." ]
def get_response(message, user_id):
    p_message = message.lower()
    
    if p_message == 'hello':
        return 'Hey there'
    if '/setup' in p_message:
        user_states[user_id] = {'step': 0, 'answers': []}
        return "Share some basic information like your age, sex, location, hobbies etc"
    if '/preference' in p_message:
        user_states[user_id] = {'step': 0, 'answers': []}
        return "What type of relationship are you looking for?"    
    if '/match' in p_message:
        # user_data = collection.find_one({"User_ID": 35})
        
        rand_idx = random.randint(0, len(preference_male)-1)
        return preference_male[rand_idx]

    if user_id in user_states:
        user_state = user_states[user_id]
        step = user_state['step']
        if step == 0:
            # handle answers for setup and preference here
            user_state['answers'].append(message)
            del user_states[user_id]
            return 'Thanks for sharing that'

    return 'I am not sure how to respond to that.'

async def send_message(message, user_message, is_private):
    try:
        response = get_response(user_message, message.author.id)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

async def create_private_text_channel(guild, user1, user2):
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user1: discord.PermissionOverwrite(read_messages=True),
        user2: discord.PermissionOverwrite(read_messages=True),
    }
    channel = await guild.create_text_channel(f'private-{user1.display_name}-{user2.display_name}', overwrites=overwrites)
    return channel
def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True  # Enable the members intent
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
        if '/like' in user_message:
            discord_user = user_message[5:].strip()
            mentioned_user = None
            print("Discord",len(discord_user))
            # Find the mentioned user
            async for member in message.guild.fetch_members(limit=None):
                print("Member name", member.display_name)
                if discord_user == member.display_name:  # Compare in lowercase
                    mentioned_user = member
                    break
            if mentioned_user:
                print(mentioned_user,message.author)
                private_channel = await create_private_text_channel(message.guild, message.author, mentioned_user)
                response = f"Starting a private server with {mentioned_user.mention}"
            else:
                response = f"User '{discord_user}' not found."

            await message.channel.send(response)
        if user_message.startswith('?'):
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)

    client.run(TOKEN)
