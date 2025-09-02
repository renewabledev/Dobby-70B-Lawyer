import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
import json
import tweepy
import re
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
bearer_token = os.getenv('bearer_token')
bearertokendobby = os.getenv('bearertokendobby')

client = tweepy.Client(bearer_token)

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def get_first_link(text):
  regex = r"https?://\S+"
  match = re.search(regex, text)
  if match:
    return match.group(0)
  else:
    return None

def extract_tweet_id(url):
    match = re.search(r"x\.com/[^/]+/status/(\d+)", url)
    if match:
        return match.group(1)
    else:
        return None
        
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Ready!')

@bot.command()
async def summary(ctx, *, link):
    tweet_id = extract_tweet_id(get_first_link(link))
    print(extract_tweet_id(get_first_link(link)))
    try:
        response = client.get_tweet(tweet_id, expansions="author_id", tweet_fields=['created_at', 'text'])
        tweet = response.data
        text = tweet.text

    except tweepy.TweepyException as e:
        print(f"Error while receiving tweet: {e}")
    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": f"Make a summary of this X post. Don't add anything of your own, make a summary of all the text I give you. Try to include absolutely all the important details. The text itself: {text}"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearertokendobby}"
    }
    response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions", headers=headers,
                                data=json.dumps(payload))
    if response.status_code == 200:
        data = json.loads(response.text)
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to get response from AI')
        print(text)
        await ctx.reply(answer)
    else:
        print(f"Error {response.status_code}: {response.text}")

@bot.command()
async def comment(ctx, *, link):
    tweet_id = extract_tweet_id(get_first_link(link))
    try:
        response = client.get_tweet(tweet_id, expansions="author_id", tweet_fields=['created_at', 'text'])
        tweet = response.data
        text = tweet.text

    except tweepy.TweepyException as e:
        print(f"Error while receiving tweet: {e}")
    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": f"Below I have left the text from the Twitter post. Study the post and try to understand what it means. Imagine that you absolutely need to comment on this post and add something to it, think about what is missing in the post. Write your comment to me, try to write it as fully and culturally as possible, without swearing. The post itself: {text}"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearertokendobby}"
    }
    response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions", headers=headers,
                                data=json.dumps(payload))
    if response.status_code == 200:
        data = json.loads(response.text)
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to get response from AI')
        await ctx.reply(answer)
    else:
        print(f"Error {response.status_code}: {response.text}")

@bot.command()
async def dobby(ctx, *, msg):
    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": f"{msg}"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearertokendobby}"
    }
    response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions", headers=headers,
                                data=json.dumps(payload))
    if response.status_code == 200:
        data = json.loads(response.text)
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to get response from AI')
        await ctx.reply(answer)
    else:
        print(f"Error {response.status_code}: {response.text}")

@bot.command()
async def doctor(ctx, *, msg):
    spis = msg.split()
    temp = spis[0]
    spis.pop(0)
    symp = ' '.join(spis)
    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": f"Hello, please help me. My temperature is - {temp}. My symptoms are - {symp}. First of all, tell me my most probable diagnosis based on my symptoms. If there are several symptoms, then list them after the most probable in the next sentence. Then explain in great detail how I should be treated for the most probable diagnosis and, if necessary, tell me what medications I need to tak, what will happen to me if I do not get treatment, and contraindications.",
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearertokendobby}"
    }
    response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions", headers=headers,
                                data=json.dumps(payload))
    if response.status_code == 200:
        data = json.loads(response.text)
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to get response from AI')
        await ctx.reply(answer)
    else:
        print(f"Error {response.status_code}: {response.text}")
    msg = await ctx.reply('Did you like the bots answer? Please rate its work.')
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')
    def check(reaction, user):
        return user == ctx.author and reaction.message == msg
    reaction, user = await bot.wait_for('reaction_add', check=check)
    if str(reaction.emoji) == '👍':
        print(f'{ctx.author} voted for "Like"')
        await ctx.reply("Thank you for your rating!")
    elif str(reaction.emoji) == '👎':
        print(f'{ctx.author} voted for "Dislike"')
        await ctx.reply("Thank you for your rating!")

@bot.command()
async def rephrase(ctx, *, msg):
    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "max_tokens": 16384,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": f"I will send you the text now, you will have to rephrase it. The words you rephrase should be very similar in meaning to those you replaced. Try not to lose the meaning of the sentence, and so that when reading it before and after the rephrase, the meaning is equally clear. The text itself: {msg}"
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearertokendobby}"
    }
    response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions", headers=headers,
                                data=json.dumps(payload))
    if response.status_code == 200:
        data = json.loads(response.text)
        answer = data.get('choices', [{}])[0].get('message', {}).get('content', 'Unable to get response from AI')
        await ctx.reply(answer)
    else:
        print(f"Error {response.status_code}: {response.text}")

@bot.event
async def on_message(message):
    if message.channel.id == 1412395978211852308: # change the channel id to your own or remove this line altogether
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type.startswith('image/'):
                    image_url = attachment.url
                    image_name = attachment.filename
                    save_path = os.path.join("images", image_name)
                    try:
                        response = requests.get(image_url)
                        response.raise_for_status()
                        with open(save_path, 'wb') as file:
                            file.write(response.content)
                        print(f"Image '{image_name}' saved to path: {save_path}")
                        payload = {
                            "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
                            "max_tokens": 16384,
                            "top_p": 1,
                            "top_k": 40,
                            "presence_penalty": 0,
                            "frequency_penalty": 0,
                            "temperature": 0.6,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": f"I had an image of a document on paper, I scanned this image with a special tool and converted it into text, so there may be errors in this text. Please check this text for legal errors and tell me if there are any, and also if there are any inaccuracies or points that need to be corrected, tell me about it. The text itself: {extract_text_from_image(save_path)}"
                                }
                            ]
                        }
                        headers = {
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {bearertokendobby}"
                        }
                        response = requests.request("POST", "https://api.fireworks.ai/inference/v1/chat/completions",
                                                    headers=headers,
                                                    data=json.dumps(payload))
                        if response.status_code == 200:
                            data = json.loads(response.text)
                            answer = data.get('choices', [{}])[0].get('message', {}).get('content',
                                                                                         'Unable to get response from AI')
                            await message.reply(answer)
                        else:
                            print(f"Error {response.status_code}: {response.text}")
                    except requests.exceptions.RequestException as e:
                        print(f"Error loading image {image_name}: {e}")
                    except Exception as e:
                        print(f"An error occurred while saving the image {image_name}: {e}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)