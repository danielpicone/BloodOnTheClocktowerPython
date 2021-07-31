# bot.py
import os

import discord
import random
import time
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

REACTIONS = {"player_role": "\U00002705",
             "night": "\U0001F319",
             "day": "\U00002600",
             "noms": "\U0001F4DC"}
REVERSE_REACTION_MAPPING = {y: x for (x,y) in REACTIONS.items()}

intents = discord.Intents.default()
intents.members = True

# client = discord.Client()
bot = commands.Bot(command_prefix="!", intents = intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

    text_channel = get_text_channel(GUILD, "moveeradmin")
    message = await text_channel.send(
        embed = discord.Embed(title = "Blood on the Clocktower commands",
                              description = "Use the emojis to move players between voice channels",
                              colour = 9021952),
                              delete_after = 3*3600)
    for name, code in REACTIONS.items():
        await message.add_reaction(code)


@bot.command(name = "99", help = "Responds with a random quote from Brooklyn 99")
@commands.has_role("Story Teller")
async def nine_nine(ctx):

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

@bot.command(name = "night")
async def night(ctx, voice_channel="Beneath the Clocktower", category="Burbs"):
    voice_channel = get_voice_channel(GUILD, voice_channel)
    cat = get_category(GUILD, category)

    num_cottages = len(cat.voice_channels)
    player_num = 1

    # Move all story tellers to first voice_channel
    for member in voice_channel.members:
        member_roles = [n.name for n in member.roles]
        if "Story Teller" in member_roles:
            await member.move_to(cat.voice_channels[0])
        elif "Player" in member_roles:
            await member.move_to(cat.voice_channels[player_num])
            player_num += 1
            if player_num > len(cat.voice_channels):
                await ctx.send("Not enough cottages for all players")

@bot.command(name = "day")
async def day(ctx, category="Burbs", voice_channel = "Beneath the Clocktower"):
    voice_channel = get_voice_channel(GUILD, voice_channel)
    cat = get_category(GUILD, category)
    for cottage_channel in cat.voice_channels:
        for member in cottage_channel.members:
            await member.move_to(voice_channel)

@bot.command(name = "noms")
async def noms(ctx, category="Ravenswood Bluff", voice_channel = "Beneath the Clocktower",
               notification_channel = "moveeradmin", delay = 10):
    voice_channel = get_voice_channel(GUILD, voice_channel)
    cat = get_category(GUILD, category)

    text_channel = get_text_channel(GUILD, notification_channel)
    col = 15105570
    message = await text_channel.send(
        embed = discord.Embed(title = "Nominations",
                              description = f"Nominations are soon, you will be automatically moved {voice_channel} in {delay} seconds",
                              colour = col))
    for t in range(0, delay):
        await message.edit(
            embed = discord.Embed(title = "Nominations",
                                  description = f"Nominations are soon, you will be automatically moved {voice_channel} in\n{delay-t} seconds",
                                  colour = col))
        time.sleep(1)

    await message.edit(
        embed = discord.Embed(title = "Nominations",
                              description = f"Please remain {voice_channel} while discussion and nominations take place",
                              colour = col), delete_after = 10)

    for day_channel in cat.voice_channels:
        for member in day_channel.members:
            await member.move_to(voice_channel)

async def player_role(ctx, user, type = "add"):
    guild = None
    for g in bot.guilds:
        if g.name == GUILD:
            guild = g
    member = guild.get_member(user.id)
    role = get_role(GUILD, "Player")

    if type == "add":
        await member.add_roles(role)
    elif type == "remove":
        await member.remove_roles(role)



@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if REVERSE_REACTION_MAPPING[reaction.emoji] == "player_role":
        await player_role(None, user, "add")
        return

    await eval(REVERSE_REACTION_MAPPING[reaction.emoji] + "(None)")
    await reaction.message.remove_reaction(reaction.emoji, user)

@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    if REVERSE_REACTION_MAPPING[reaction.emoji] == "player_role":
        await player_role(None, user, "remove")
        return

def get_voice_channel(guild, channel):
    for g in bot.guilds:
        if g.name == guild:
            for ch in g.voice_channels:
                if ch.name == channel:
                    return ch

def get_text_channel(guild, channel):
    for g in bot.guilds:
        if g.name == guild:
            for ch in g.text_channels:
                if ch.name == channel:
                    return ch

def get_category(guild, category):
    for g in bot.guilds:
        if g.name == guild:
            for cat in g.categories:
                if cat.name == category:
                    return cat

def get_role(guild, role_name):
    for g in bot.guilds:
        if g.name == guild:
            for role in g.roles:
                if role.name == role_name:
                    return role

bot.run(TOKEN)
