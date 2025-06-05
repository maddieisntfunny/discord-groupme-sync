from json import loads
from multiprocessing import Process
import requests
from flask import Flask, request

DISC_WEBHOOK = "url"
app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    message_object = loads(request.data)
    if message_object['name'] == 'Discord':
        print('bot sent this, exiting out')
        return ''
    print(message_object)
    if message_object['attachments'] and message_object['attachments'][0]['type'] == "image":
        url = ''
        for attachment in message_object['attachments']:
            url = url + ' ' + attachment['url']
        print(url)
        response = requests.post(
	    DISC_WEBHOOK, data={
                'username': message_object['name'],
                'content': message_object['text'] + ' ' + url,
                'avatar_url': message_object['avatar_url']
            }
        )
        print(response.text)
    else:
        requests.post(
            DISC_WEBHOOK, data={
                'username': message_object['name'],
                'content': message_object['text'],
                'avatar_url': message_object['avatar_url']
            }
        )
    return ''


def main(*args, **kwargs):
    Process(target=app.run, args=args, kwargs=kwargs).start()