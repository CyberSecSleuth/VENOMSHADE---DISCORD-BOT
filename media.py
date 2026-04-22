import discord
import re
import storage

from config import SOCIAL_CHANNEL_ID


def get_post_counter():
    return storage.get_state().get("post_counter", 0)


POST_COUNTER = get_post_counter()


def save_post_counter(value):
    storage.update_state("post_counter", value)

INSTAGRAM_REGEX = r"(?:https?://)?(?:www\.)?instagram\.com/(reel|p)/([A-Za-z0-9_-]+)"

TIKTOK_REGEX = r"(https?://)?(www\.)?(tiktok\.com)/.+"

def extract_instagram_data(link: str):
    match = re.search(INSTAGRAM_REGEX, link)
    if not match:
        return None

    content_type = match.group(1)
    media_id = match.group(2)

    return content_type, media_id


async def handle_media(bot, message: discord.Message):

    if message.channel.id != SOCIAL_CHANNEL_ID:
        return False

    if message.author == bot.user:
        return False

    if message.author.bot:
        try:
            await message.delete()
        except:
            pass
        return True

    content = message.content.strip()

    insta_data = extract_instagram_data(content)

    if insta_data:
        global POST_COUNTER
        POST_COUNTER += 1
        save_post_counter(POST_COUNTER)

        content_type, media_id = insta_data

        media_type = "REEL" if content_type == "reel" else "POST"
        formatted_no = f"{POST_COUNTER:03d}"

        embed = discord.Embed(
            color=discord.Color.from_rgb(255, 105, 180)
        )

        embed.description = (
            f"# ✦ {media_type} 𖹭 #{formatted_no}\n\n"
            f"**𐀪 Shared by:** {message.author.mention}"
        )
        
        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.set_footer(text="Venomshade Media System")

        await message.channel.send(embed=embed)

        new_url = f"[{media_type}](https://kkinstagram.com/{content_type}/{media_id})"

        sent_msg = await message.channel.send(new_url)
        await message.channel.send("‎ ‎ ‎ ‎ ‎  ✦•┈๑⋅⋯ ⋯⋅๑┈•✦")

        try:
            await sent_msg.add_reaction("👍")
            await sent_msg.add_reaction("👎")
        except:
            pass

        try:
            await message.delete()
        except:
            pass

        return True

    if message.mentions:
        return False

    try:
        await message.delete()
    except:
        pass

    return True