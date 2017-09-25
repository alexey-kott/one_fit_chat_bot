import re
import datetime
import json
from channels import Group
from channels.sessions import channel_session


from .models import User
from .models import Message
from .models import Trainer

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


@channel_session
def ws_connect(message):
    # prefix, label = message['path'].strip('/').split('/')
    print("WS_CONNECT")
    Group('admin', channel_layer=message.channel_layer).add(message.reply_channel)
    response = []
    item = dict()
    item['type'] = 'trainers'
    item['data'] = [t for t in Trainer.objects.values()]
    response.append(item)
    item = dict()
    item['type'] = 'sms'
    item['data'] = [sms for sms in Message.objects.values()]
    response.append(item)
    item = dict()
    item['type'] = 'userlist'
    item['data'] = [u for u in User.objects.values()]
    response.append(item)
    Group('admin', channel_layer=message.channel_layer).send({'text': json.dumps(response, default = datetime_handler)})


@channel_session
def ws_receive(message):
	print("WS_RECEIVE")
	data = json.loads(message['text'])
	if data['type'] == "sms": # слишком много "сообщений". сообщения от тренера пользователю будем называть sms-ками
		m = Message()
		m.send_message(data['sender'], data['receiver'], data['text'])
	Group('admin', channel_layer=message.channel_layer).send({'text':message['text']})


@channel_session
def ws_disconnect(message):
	print("WS_DISCONNECT")
	print(message)