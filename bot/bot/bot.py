import telebot
from telebot import types
import sqlite3 as sqlite
import re
import config as cfg
from peewee import *
from playhouse.sqlite_ext import *
import strings as s # все строки хранятся здесь
from actions import *

# README
#
# Shortcuts:
#	sid 	= sender chat id
#	m 		= message
#	cog 	= create_or_get
#	c 		= call

bot = telebot.TeleBot(cfg.token)
db = SqliteDatabase('bot.db')

sid = lambda m: m.chat.id # лямбды для определения адреса ответа
uid = lambda m: m.from_user.id
cid = lambda c: c.message.chat.id



class BaseModel(Model):
	class Meta:
		database = db

class User(BaseModel):
	user_id 	= IntegerField(unique = True)
	username	= TextField(null = True)
	first_name 	= TextField(null = True)
	last_name   = TextField(null = True)
	email		= TextField(null = True)
	state		= TextField(default = s.default)

	def cog(user_id, username, first_name, last_name):
		try:
			with db.atomic():
				return User.create(user_id = user_id, username = username, first_name = first_name, last_name = last_name)
		except:
			return User.select().where(User.user_id == user_id).get()


class Routing(BaseModel):
	state 		= TextField()
	decision 	= TextField() # соответствует либо атрибуту data в инлайн кнопках, 
							  # либо специальному значению text, которое соответствует любому текстовому сообщению
	action		= TextField()

	class Meta:
		primary_key = CompositeKey('state', 'decision')



# _____________ ACTIONS


def cancel(c):
	u = User.get(user_id = cid(c))
	u.state(s.canceled)
	u.save()
	t = bot.send_message(cid(c), s.canceled_course)

def confirm_name(c):
	u = User.get(user_id = cid(c))
	u.state = s.lets_confirm_name
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.my_name_is_btn.format(u.first_name), callback_data = s.agree)
	keyboard.add(agree_btn)
	bot.send_message(cid(c), s.confirm_name.format(u.first_name), reply_markup = keyboard)

def confirm_last_name(m = None, c = None): # получает имя (текстом) или подтверждение того, что мы правильно записали его имя
	if m != None:
		u = User.get(user_id = uid(m))
		u.first_name = m.text
		u.state = s.lets_confirm_last_name
		u.save()
	else:
		u = User.get(user_id = cid(c))
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.my_last_name_is_btn.format(u.last_name), callback_data = s.agree)
	keyboard.add(agree_btn)
	bot.send_message(cid(c), s.confirm_last_name.format(u.last_name), reply_markup = keyboard)


# _____________ END ACTIONS



@bot.message_handler(commands = ['init'])
def init(m):
	User.create_table(fail_silently = True)
	# Routing.create_table(fail_silently = True)


@bot.message_handler(commands = ['start'])
def start(m):
	u = User.cog(user_id = uid(m), username = m.from_user.username, first_name = m.from_user.first_name, last_name = m.from_user.last_name)
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.agree_btn, callback_data = s.agree)
	disagree_btn = types.InlineKeyboardButton(text = s.disagree_btn, callback_data = s.disagree)
	more_btn = types.InlineKeyboardButton(text = s.more_btn, callback_data = s.more)
	keyboard.add(agree_btn)
	keyboard.add(disagree_btn)
	keyboard.add(more_btn)
	bot.send_message(uid(m), s.greeting, reply_markup = keyboard, parse_mode = "Markdown")


@bot.callback_query_handler(func=lambda call: True)
def clbck(c):
	u = User.get(user_id = cid(c))
	r = Routing.get(state = u.state, decision = c.data)
	keyboard = types.InlineKeyboardMarkup()
	bot.edit_message_reply_markup(chat_id = cid(c), message_id = c.message.message_id, reply_markup = keyboard)
	bot.answer_callback_query(callback_query_id = c.id, show_alert = True)

	# eval(r.action)(c = c)

	try: # на случай если action не определён в таблице роутинга
		eval(r.action)(c = c)
	except Exception as e:
		print(e)
		print(s.action_not_defined)

	# 	print(c)



@bot.message_handler(content_types = ['text'])
def action(m):
	u = User.cog(user_id = uid(m))
	r = Routing.get(state = u.state, decision = 'text')
	try: # на случай если action не определён в таблице роутинга
		eval(r.action)(m = m)
	except:
		print(s.action_not_defined)
		print(m)







if __name__ == '__main__':
	bot.polling(none_stop=True)