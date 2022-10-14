# bot.py
import os

import discord
from dotenv import load_dotenv
import requests

#DMR: 514059860489404417
SUPPORTED_SERVERS = [610972034738159617]
BASE_API_URL = "https://dmr.nblock.online/api/"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = discord.Bot()

def get_tag_list():
    r = requests.get(f"{BASE_API_URL}GetAllItems")
    if not r.status_code == 200 or r.text == "null" or len(r.json()) == 0:
        return []
    else:
        full_tag_list = []
        for result in r.json():
            for tag in result['tags']:
                full_tag_list.append(tag)
        return set(full_tag_list)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

search = bot.create_group("search", "Search for items on the drive")

@search.command(name="name", description="Search for items in the API by name", guild_ids=SUPPORTED_SERVERS)
async def name_search(ctx, name: discord.Option(str)):
    r = requests.get(f"{BASE_API_URL}GetItem?name={name}")
    if r.status_code == 200:
        embed = discord.Embed(title=f"Search Results for \"{name}\"")
        if r.text == "null" or len(r.json()) == 0:
            embed.description = "No results found."
        else:
            embed.description = f"{len(r.json())} results found for {name}:"
            for result in r.json():
                print(result)
                embed.add_field(name=result['primary_name'], value=f"**aka:** {list(result['names'])}\n\n**Tags:** {list(result['tags'])}\n\n**Link:** {result['link']}", inline=False)
        await ctx.respond(embed=embed)
    elif r.status_code == 404 or r.text.startswith("Cannot GET"):
        await ctx.respond("DMR Drive API is not up at the moment. Try again later.")
    else:
        await ctx.respond(f"Unhanded response code {r.status_code}. Contact Bytestorm or another bot maintainer.")
@search.command(name="tags", description="Search for items in the API by tag(s). [Tag list should be comma-separated]")
async def tag_search(ctx, tags: discord.Option(str)):
    in_tags = [s.strip() for s in tags.split(',')]
    tagParam = tags.strip()
    if len(in_tags) > 1:
        tagParam = in_tags[0]
        for t in in_tags[1:]:
            tagParam += "," + t
    print(f"{BASE_API_URL}GetItem?tags={tagParam}")
    r = requests.get(f"{BASE_API_URL}GetItem?tags={tagParam}")
    if r.status_code == 200:
        embed = discord.Embed(title=f"Search Results for tags \"{tagParam}\"")
        if r.text == "null" or len(r.json()) == 0:
            embed.description = "No results found."
        else:
            embed.description = f"{len(r.json())} results found for {tagParam}:"
            for result in r.json():
                print(result)
                embed.add_field(name=result['primary_name'], value=f"**aka:** {list(result['names'])}\n\n**Tags:** {list(result['tags'])}\n\n**Link:** {result['link']}", inline=False)
        await ctx.respond(embed=embed)
    elif r.status_code == 404 or r.text.startswith("Cannot GET"):
        await ctx.respond("DMR Drive API is not up at the moment. Try again later.")
    else:
        await ctx.respond(f"Unhanded response code {r.status_code}. Contact Bytestorm or another bot maintainer.")
@bot.command(name="get_taglist", description="Returns a list of all tags currently used in the API")
async def cmd_get_tags(ctx):
    taglist = get_tag_list()
    await ctx.respond(str(taglist))
    
bot.run(TOKEN)
