import os
import channels.asgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "one_fit_chat_bot.settings")
channel_layer = channels.asgi.get_channel_layer()