import os
import requests
import discord
from discord.ext import commands
import yaml
import openai
import asyncio
import re


def load_config():
    with open("config.yml", "r") as config_file:
        return yaml.safe_load(config_file)

def save_config(config):
    with open("config.yml", "w") as config_file:
        yaml.dump(config, config_file)

config = load_config()

openai.api_key = config.get("openai_api_key")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def set_channel(ctx):
    channel_id = ctx.channel.id
    config["discord_channel_id"] = str(channel_id)
    save_config(config)
    await ctx.send(f"The current channel has been set as the chatbot's channel.")

@bot.command()
async def remove_channel(ctx):
    config["discord_channel_id"] = None
    save_config(config)
    await ctx.send(f"The configured channel has been removed.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    discord_channel_id = config.get("discord_channel_id")
    if str(message.channel.id) == discord_channel_id:


        input = message.content + "\n"
        response = openai.Completion.create(
          model=config.get("openai_model"),
          prompt=input,
          temperature=0.5,
          max_tokens=2099,
          top_p=0.3,
          frequency_penalty=2,
          presence_penalty=0.4
        )


        output = response['choices'][0]['text'] + "\n"

        filtered_text = filter_swears(output)

        await asyncio.sleep(1)
        await message.channel.send(filtered_text)
    await bot.process_commands(message)

bot.run(config["discord_token"])

