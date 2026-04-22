import aiohttp
import discord
from random import randint
from discord.ext import commands

FACT_API_URL = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"
INSULT_API_URL = "https://evilinsult.com/generate_insult.php?lang=en&type=json"


async def fetch_insult():
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(INSULT_API_URL, headers=headers) as resp:                
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("insult", "No insult found")
                return None
    except Exception as e:
        print(f"[INSULT] Error: {e}")
        return None


def is_bot_user(user) -> bool:
    return user.bot


async def fetch_random_fact():
    headers = {"Accept": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(FACT_API_URL, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("text", "No fact found")
            return None


@discord.app_commands.command(name="fact", description="Get a random fact")
async def fact_command(interaction: discord.Interaction):
    await interaction.response.defer()

    fact = await fetch_random_fact()

    if not fact:
        return await interaction.followup.send(
            "Failed to fetch a fact. Try again later.",
            ephemeral=True
        )

    embed = discord.Embed(
        description=f"## DO YOU KNOW THAT\n> ### {fact}\n## Isn't that concerning???",
        color=discord.Color(randint(0, 0xFFFFFF)),
    )

    embed.set_footer(
        text="Venomshade Facts System",
        icon_url=interaction.user.display_avatar.url
    )

    await interaction.followup.send(embed=embed)


@discord.app_commands.command(name="insult", description="Insult someone!")
async def insult_command(interaction: discord.Interaction, user: discord.Member = None):
    if user and is_bot_user(user):
        return await interaction.response.send_message(
            "I don't insult bots. They are my brothers and sisters.",
            ephemeral=True
        )

    insult = await fetch_insult()
    if not insult:
        return await interaction.response.send_message(
            "Failed to fetch an insult. Try again later.",
            ephemeral=True
        )

    if user:
        await interaction.response.send_message(f"{user.mention} {insult}")
    else:
        await interaction.response.send_message(f"{interaction.user.mention} {insult}")


def setup(bot):
    bot.add_command(reply_command)
    return fact_command, insult_command


@commands.command(name="insult")
async def reply_command(ctx: commands.Context):
    if not ctx.message.reference:
        return

    if ctx.message.author.bot:
        return

    try:
        referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    except:
        return

    if referenced_message.author.bot:
        return await referenced_message.reply("I don't insult bots. They are my brothers")

    insult = await fetch_insult()
    if not insult:
        return await referenced_message.reply("Failed to fetch an insult. Try again later.")

    await referenced_message.reply(f"{insult}")
    await ctx.message.delete()
