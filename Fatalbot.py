'''
Title: FatalBot.py
Purpose : To moderate, assign roles, do trivia and much more in discord servers. 
Date: 10/27/2023
Author: Christian Rock, rockcm@etsu.edu. 2023
'''
import os
import requests
import random
import discord
import re
from discord.ext import commands
import yt_dlp as youtube_dl
import ffmpeg

TOKEN = ''
SERVER_ID = '647932338164072468'
KICK_PHRASE = 'fuck'
KICK_REASON = 'blasphemy'

intents = discord.Intents.all()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(intents=intents, command_prefix='!')

#states bot connected to system
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


# create channel command
@bot.command(name='create-channel') # name of the command !create-channel test
@commands.has_role('Admin') #ensure the caller has correct privelage
async def create_channel(ctx, channel_name): #defines params and ctx
    category_name = 'Text Channels'  #the channel category that the new channel will appear in

    # Find the category by name
    category = discord.utils.get(ctx.guild.categories, name=category_name)

    if category:
        new_channel = await ctx.guild.create_text_channel(channel_name, category=category) # cretes the channel 
        await ctx.send(f"Created a new text channel in the '{category_name}' category: {new_channel.mention}") #message to let you know it is created 
    else:
        await ctx.send(f"'{category_name}' category not found.")


#create voice channel command. 

@bot.command(name='create-voice')
@commands.has_role('Admin')
async def create_voice_channel(ctx, channel_name):
    category_name = 'Voice Channels'  # The category name you want to use

    # Find the category by name
    category = discord.utils.get(ctx.guild.categories, name=category_name)

    if category:
        new_channel = await ctx.guild.create_voice_channel(channel_name, category=category)
        await ctx.send(f"Created a new voice channel in the '{category_name}' category: {new_channel.mention}")
    else:
        await ctx.send(f"'{category_name}' category not found.")

#delete channel specified if user has admin role
@bot.command(name='delete-channel')
@commands.has_role('Admin')
async def delete_channel(ctx, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    
    if existing_channel:
        await existing_channel.delete()
        await ctx.send(f'Channel "{channel_name}" has been deleted.')
    else:
        await ctx.send(f'No channel named "{channel_name}" was found.')

@bot.command(name='delete-voice-channel')
@commands.has_role('Admin')
async def delete_voice_channel(ctx, channel_name):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.voice_channels, name=channel_name)
    
    if existing_channel:
        await existing_channel.delete()
        await ctx.send(f'Voice channel "{channel_name}" has been deleted.')
    else:
        await ctx.send(f'No voice channel named "{channel_name}" was found.')




@bot.command()
async def assign_role(ctx, user: discord.Member, role_name: str):
    
    if ctx.author.guild_permissions.administrator:
        # Gets the role name
        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if role:
            # Check if the user already has role
            if role in user.roles:
                await ctx.send(f"{user.mention} already has {role_name} role.")
            else:
                # Assign role to the user
                await user.add_roles(role)
                await ctx.send(f"{user.mention} has been given {role_name} role.")
        else:
            await ctx.send(f"Role '{role_name}' not found.")
    else:
        await ctx.send("You don't have permission to use this command.")
#potential Error hadnling 
@assign_role.error
async def assign_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command. You must be an administrator.")


@bot.event
async def on_raw_reaction_add(payload):
    message_id = 1166257753107468308  
    emoji_to_role = {
        "😂": "",
        "🤘": "",
        "🎸": "",
        "🥁": "",
        "🎤": "",
        "🍔": "",
        "🚀": "",
        "🌈": "",
        "🏝️": "",
        "🌊": "",
        "⚫": "",
        "🎹": "",
        "🧠": "",
        
       
    }

    if payload.message_id == message_id:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if member:
            emoji = str(payload.emoji)
            role_name = emoji_to_role.get(emoji)

            if role_name:
                role = discord.utils.get(guild.roles, name=role_name)

                if role:
                    await member.add_roles(role)
                    print(f"Assigned {role_name} to {member.display_name}")



#tells the user what categories are available for trivia
@bot.command(name='triviacategories')
async def triviacats(ctx):
    validCategories = 'artliterature, language, sciencenature, general, fooddrink, peopleplaces, geography, historyholidays, entertainment, toysgames, music, mathematics, religionmythology, sportsleisure'
    await ctx.send(validCategories)

@bot.command(name='trivia')
async def trivia(ctx, category = ""):
    validCategories = ['','artliterature', 'language', 'sciencenature','general','fooddrink','peopleplaces','geography','historyholidays','entertainment','toysgames','music','mathematics','religionmythology','sportsleisure']
    if category in validCategories:
        api_url = 'https://api.api-ninjas.com/v1/trivia?category={}'.format(category)
        response = requests.get(api_url, headers={''})
        if response.status_code == requests.codes.ok:
            info = response.json()
            #idk why this is a for loop but it won't work not in a for loop
            for q in info:
                question = q['question']
                #make sure the user you are checking the response of is the one that asked for a trivia question
                def check(response):
                    return response.author == ctx.author
                await ctx.send(question)
                #store user response
                response = await bot.wait_for("message", check=check)
                #respond based on if the user had the write answer or not
                for a in info:
                    if(response.content.lower() == a['answer'].lower()):
                        await ctx.send("You are correct!")
                    else:
                        answer = a['answer']
                        await ctx.send(f"Wrong! {answer} was the correct answer.")
    else: #if the user gave invalid category
        await ctx.send("Invalid category. Please call !triviacategories to view all possible categories.")


#tells when a role has been manually added not through react
@bot.event
async def on_member_update(before, after):
    # Check to see if a role was added to the user
    added_roles = set(after.roles) - set(before.roles)

    if added_roles:
        for role in added_roles:
            role_name = role.name  # Get the name of the added role
            member = after  # The user who receives role

            
            channel = member.guild.get_channel(1161377218723856509)  

            if channel:
                
                await channel.send(f"Assigned '{role_name}' to {member.mention}")

@bot.command(name='metallica-poll')
async def metallica_poll(ctx):
    # Define the question and answer options for the poll
    question = "What is your favorite Metallica album?"
    options = ["Kill 'Em All", "Ride the Lightning", "Master of Puppets", "…And Justice for All", "Metallica (The Black Album)", "Load", "Reload", "St. Anger", "Death Magnetic", "Hardwired... to Self-Destruct"]

    # Create the poll embed
    poll_embed = discord.Embed(
        title="Metallica Album Poll",
        description=question,
        color=0xffd700  # Set the color to a gold-like color
    )

    # Add the answer options to the embed
    for i, option in enumerate(options, 1):
        poll_embed.add_field(name=f"Option {i}", value=option, inline=False)

    # Send the poll and record the message
    poll_message = await ctx.send(embed=poll_embed)

    # Add reactions to the message for each option
    for i in range(1, len(options) + 1):
        await poll_message.add_reaction(f"{i}\N{COMBINING ENCLOSING KEYCAP}")

    await ctx.send("Poll created! React with the corresponding emoji to vote for your favorite Metallica album.")





@bot.event
async def on_member_join(member):
    # Define the welcome message
    welcome_message = f"Welcome, {member.mention}, to our server! We're glad to have you here. Please make yourself at home and don't hesitate to introduce yourself and get to know our community."

    # Specify the channel where you want to send the welcome message
    welcome_channel = member.guild.get_channel(647932338164072472)  # Replace YOUR_WELCOME_CHANNEL_ID with the actual channel ID

    if welcome_channel:
        await welcome_channel.send(welcome_message)

@bot.command()
async def dadjoke(ctx):
    limit = 1
    api_url = f'https://api.api-ninjas.com/v1/dadjokes?limit={limit}'
    headers = {'X-Api-Key': ''}

    response = requests.get(api_url, headers=headers)

    if response.status_code == requests.codes.ok:
        jokes = response.json()
        joke_texts = [joke['joke'] for joke in jokes]
        jokes_text = '\n'.join(joke_texts)
        await ctx.send(f"Here's a dad joke:\n{jokes_text}")
    else:
        await ctx.send(f"Error: {response.status_code} {response.text}")




@bot.event
async def on_message(message):
    # Check if the message author is the specific user you want to respond to
    if message.author.id == 192824520808202240:  # Replace with the user's actual ID
        # Send "shut up" as a response
        await message.channel.send("shut up MoleK")

    # Continue processing other messages as usual
    if message.author == bot.user:
        return
    if "weezer" in message.content.lower():
        channel = message.channel
        await channel.send(f"https://media.tenor.com/NFr67X_ELO0AAAAC/u-just-got-weezered-weezer.gif")
    if KICK_PHRASE in message.content.lower():
        member = message.author
        try:
            
            channel = discord.utils.get(message.guild.text_channels, name='general')  
            invite = await channel.create_invite(reason="Re-invite for kicked member", max_uses=1, unique=True)
            
            
            await member.send(f"{KICK_REASON} Here's an invite to come back: {invite.url}")
            
            
            await member.kick(reason=KICK_REASON)
        except discord.Forbidden:
            
            print(f"Couldn't kick {member.name}. Check bot permissions.")

    await bot.process_commands(message)



@bot.command()
async def join(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        voice_channel = await channel.connect()
    else:
        await ctx.send("You are not in a voice channel.")


@bot.command()
async def play(ctx, url):
    if ctx.voice_client:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            ctx.voice_client.stop()
            ctx.voice_client.play(discord.FFmpegPCMAudio(url2))
    else:
        await ctx.send("I'm not in a voice channel.")
    
bot.run(TOKEN)

