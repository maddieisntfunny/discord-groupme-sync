import json
from os import path
from sys import exit
from io import BytesIO
from random import randint
from multiprocessing import Process
from typing import List, Union, Optional, Callable
import requests
from discord.ext import commands
from aiohttp import ClientSession
from discord import Attachment, Message

gm_url = 'https://api.groupme.com/v3/bots/post'
sent_buffer = []
DC_BOT_TOKEN = "dc_bot_token"
GM_BOT_ID = "gm_bot_id"
GM_BOT_TOKEN = "gm_bot_token"
DC_CHANNEL_ID = "dc_channel_id"


async def post(session: ClientSession, url: str, payload: Union[BytesIO, dict], headers: Optional[dict] = None) -> str:
    response = requests.post(url, json=payload)
    print(response.text)

def get_prefix(bot_instance: commands.Bot, message: Message) -> Callable[[commands.Bot, Message], list]:
    prefixes = ['>']
    return commands.when_mentioned_or(*prefixes)(bot_instance, message)
bot = commands.Bot(command_prefix=get_prefix)

async def send_message(message: Message) -> str:
    text = f'{message.author.display_name}: {message.content}'.strip()
    sent_buffer.append(text)
    if len(sent_buffer) > 10:
        sent_buffer.pop(0)
    msgtext = message.author.display_name + ': ' + message.content
    payload = {
        'bot_id': GM_BOT_ID,
        'text': msgtext
    }
    att = await process_attachments(message.attachments)
    if att is not None:
        # support up to 3 image attachments in 1 message because I'm lazy
        # yes I know this is fucking horrible
        print('num attach')
        print(len(att))
        if len(att) == 1:
            payload = {
                'bot_id': GM_BOT_ID,
                'text': msgtext,
                'attachments': [
                    {
                        'type': 'image',
                        'url': att[0]['url']
                    }
                ]
            }
        elif len(att) == 2:
            payload = {
                'bot_id': GM_BOT_ID,
                'text': msgtext,
                'attachments': [
                    {
                        'type': 'image',
                        'url': att[0]['url']
                    },
                    {
                        'type': 'image',
                        'url': att[1]['url']
                    }

                ]
            }
        else:
            payload = {
                'bot_id': GM_BOT_ID,
                'text': msgtext,
                'attachments': [
                    {
                        'type': 'image',
                        'url': att[0]['url']
                    },
                    {
                        'type': 'image',
                        'url': att[1]['url']
                    },
                    {
                        'type': 'image',
                        'url': att[2]['url']
                    }
                ]
            }
    print(payload)
    async with ClientSession() as session:
        return await post(session, gm_url, payload)


async def process_attachments(attachments: List[Attachment]) -> str:
    if not attachments:
        return
    att = {}
    i = 0
    for attachment in attachments:
        groupme_images_url = 'https://image.groupme.com/pictures'
        if not attachment.filename.endswith(('jpeg', 'jpg', 'png', 'gif')):
            return
        extension = attachment.filename.partition('.')[-1]
        if extension == 'jpg':
            extension = 'jpeg'
        imgurl = attachment.url
        print('image url ' + imgurl)
        headers = {
            'X-Access-Token': GM_BOT_TOKEN,
            'Content-Type': f'image/jpeg'
        }
        getresp = requests.get(imgurl)
        #print('get response: ' + getresp.text)
        postresp = requests.post(groupme_images_url, data=getresp.content, headers=headers)
        print('post response: ' + postresp.text)
        finalurl = json.loads(postresp.content)['payload']['picture_url']
        print('final image url: ' + finalurl)
        att.update({i: {'url': finalurl}})
        i = i + 1
    print('att: ')
    print(att)
    return att

@bot.event
async def on_ready() -> None:
    print('-------------\nBot is ready!\n-------------')


@bot.event
async def on_message(message: Message) -> None:
    if message.content == '>pet the bot':
        await message.reply(':3')
    if message.channel.id == DC_CHANNEL_ID:
        if not message.author.bot:
            print(await send_message(message))
        elif message.content in sent_buffer:
            await message.delete()


def main():
    Process(target=bot.run, args=(DC_BOT_TOKEN,)).start()