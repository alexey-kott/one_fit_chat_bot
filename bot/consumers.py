import re
import datetime
import json
from channels import Group
from channels.sessions import channel_session


from .models import User

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


@channel_session
def ws_connect(message):
    # prefix, label = message['path'].strip('/').split('/')
    print("WS_CONNECT")
    users = [u for u in User.objects.values()]
    Group('admin', channel_layer=message.channel_layer).add(message.reply_channel)
    Group('admin', channel_layer=message.channel_layer).send({'text': json.dumps(users, default = datetime_handler)})

@channel_session
def ws_receive(message):
	print("WS_RECEIVE")
	print(message)


@channel_session
def ws_disconnect(message):
	print("WS_DISCONNECT")
	print(message)