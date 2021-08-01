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

PLAYING_MESSAGE = "Blood on the Clocktower"

NOTIFICATION_CHANNEL = "commands"

intents = discord.Intents.default()
intents.members = True

# client = discord.Client()
bot = commands.Bot(command_prefix="!", intents = intents)

MESSAGE_IDS = []

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

    game = discord.Game(PLAYING_MESSAGE)
    await bot.change_presence(activity = game)

    text_channel = get_text_channel(GUILD, NOTIFICATION_CHANNEL)
    message = await text_channel.send(
        embed = discord.Embed(title = "Blood on the Clocktower commands",
                              description = "Click the emojis to move players between voice channels\n" + \
                                             "\U00002705:  gives the user the `Player` role, and unclicking removes the `Player` role\n" + \
                                             "\U0001F319:  moves all users marked with the `Player` or `Story Teller` role to individual cottages\n" + \
                                             "\U00002600:  moves all users marked with the `Player` or `Story Teller` role to `Beneath the Clocktower`\n" + \
                                             "\U0001F4DC:  warns all users that nominations are soon and will move all users in `Ravenswood Bluff` to `Beneath the Clocktower`",
                              colour = 2123412))
    for name, code in REACTIONS.items():
        await message.add_reaction(code)

    return message


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
async def night(ctx, voice_channel="Beneath the Clocktower", category_from = "Ravenswood Bluff", category_to="Burbs"):
    voice_channel = get_voice_channel(GUILD, voice_channel)
    cat_from = get_category(GUILD, category_from)
    cat_to = get_category(GUILD, category_to)

    num_cottages = len(cat_to.voice_channels)
    player_num = 1

    # Get all members in Ravenswood Bluff
    members = []
    for vc in cat_from.voice_channels:
        members.extend(vc.members)

    # guild = get_guild(GUILD)

    # Move all story tellers to first voice_channel
    # for member in voice_channel.members:
    for member in members:
        member_roles = [n.name for n in member.roles]
        # print("Story Teller" in member_roles)
        # print(discord.utils.get(guild.roles, name = "Story Teller") in member.roles)
        if "Story Teller" in member_roles:
            await member.move_to(cat_to.voice_channels[0])
        elif "Player" in member_roles:
            await member.move_to(cat_to.voice_channels[player_num])
            player_num += 1
            if player_num > len(cat_to.voice_channels):
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
               notification_channel = NOTIFICATION_CHANNEL, delay = 10):
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
    text_channel = get_text_channel(GUILD, NOTIFICATION_CHANNEL)
    if user.bot:
        return

    if REVERSE_REACTION_MAPPING[reaction.emoji] == "player_role":
        await player_role(None, user, "add")
        return

    if "Story Teller" in [role.name for role in user.roles]:
        await eval(REVERSE_REACTION_MAPPING[reaction.emoji] + "(None)")
    else:
        await text_channel.send(user.display_name + " is trying to move members without the Story Teller role, shame!")

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

def get_guild(guild = GUILD):
    for guild in bot.guilds:
        if guild.name == GUILD:
            return guild

bot.run(TOKEN)
