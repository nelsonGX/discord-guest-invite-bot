import discord
import os
import time
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
if token == None:
    print("DISCORD_TOKEN is not set in the environment variables.")
    exit(1)

client = discord.Client(intents=discord.Intents.all())

vc_users = {}
cached_invite_links = {}
channel_last_create = {}

@client.event
async def on_ready():
    print("Bot has started")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if client.user.mentioned_in(message): # type: ignore
        user = message.author
        if user.id not in vc_users:
            await message.reply("你不在語音頻道裡!(或嘗試重新加入語音頻道)")
            return
        async with message.channel.typing():
            user_channel_id = vc_users[user.id]
            
            if user_channel_id in cached_invite_links and channel_last_create[user_channel_id] - time.time() < 60 * 60 * 12:
                return await message.reply(cached_invite_links[user_channel_id])

            user_channel = client.get_channel(user_channel_id)
            if type(user_channel) == discord.VoiceChannel:
                invite = await user_channel.create_invite(
                    max_age=60 * 60 * 24,
                    max_uses=0,
                    temporary=True
                )
                invite_url = invite.url
                cached_invite_links[user_channel_id] = invite_url
                channel_last_create[user_channel_id] = time.time()
                await message.reply(invite_url)

@client.event
async def on_voice_state_update(member, before, after):
    global vc_users
    if after.channel != None:
        vc_users[member.id] = after.channel.id
    else:
        vc_users.pop(member.id, None)
    print(vc_users)

client.run(token=token)