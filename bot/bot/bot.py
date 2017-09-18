import telebot
from telebot import types
import sqlite3 as sqlite
import re
import config as cfg
from peewee import *
from playhouse.sqlite_ext import *
import strings as s # все строки хранятся здесь
from actions import *
import check
import threading
from functions import send_mail


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
	user_id 	   = IntegerField(unique = True)
	username	   = TextField(null = True)
	first_name 	   = TextField(null = True)
	last_name      = TextField(null = True)
	sex 		   = TextField(null = True)
	age			   = IntegerField(null = True)
	email		   = TextField(null = True)
	state		   = TextField(default = s.default)
	trainer_id     = IntegerField(null = True)
	city 		   = TextField(null = True)
	job 		   = TextField(null = True)
	height 		   = IntegerField(null = True)
	weight		   = FloatField(null = True)
	target_weight  = TextField(null = True)
	methodologies  = TextField(null = True) # какими методиками пользовались
	most_difficult = TextField(null = True) # что было самое сложное?
	was_result	   = TextField(null = True) # был ли результат?
	why_fat_again  = TextField(null = True) # почему вес снова возвращался, как вы думаете?




	def cog(user_id, username = None, first_name = None, last_name = None):
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


class Trainer(BaseModel):
	first_name	= TextField()
	last_name 	= TextField()
	photo 		= TextField()




# _____________ FUNCTIONS

def delay(func): # отсылка сообщений с задержкой
    def delayed(*args, **kwargs):
        chat_id, m = args
        u = User.get(user_id = chat_id)
        u.state = s.stop
        u.save()
        timer = threading.Timer(kwargs['delay'], func, args=args, kwargs=kwargs)
        timer.start()
    return delayed


@delay
def send_message_delay(chat_id, m, state=None, delay = 0, reply_markup=None, disable_notification=None):
	u = User.get(user_id = chat_id)
	if state != None:
		u.state = state
	u.save()
	bot.send_message(chat_id, m, reply_markup=reply_markup, parse_mode='Markdown', disable_notification=disable_notification)




# _____________ END FUNCTIONS

# _____________ ACTIONS


def cancel(chat_id, c):
	u = User.get(user_id = cid(c))
	u.state = s.stop
	u.save()
	bot.send_message(chat_id, s.canceled_course)


def confirm_name(chat_id, c):
	u = User.get(user_id = cid(c))
	u.state = s.lets_confirm_name
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.my_name_is_btn.format(u.first_name), callback_data = s.agree)
	keyboard.add(agree_btn)
	bot.send_message(chat_id, s.confirm_name.format(u.first_name), reply_markup = keyboard)


def confirm_last_name(chat_id, m = None, c = None): # получает имя (текстом) или подтверждение того, что мы правильно записали его имя
	if m != None:
		u = User.get(user_id = uid(m))
		u.first_name = m.text
		keyboard = types.InlineKeyboardMarkup()
		bot.edit_message_reply_markup(uid(m), message_id = int(m.message_id) - 1, reply_markup = keyboard)
	else:
		u = User.get(user_id = cid(c))
	u.state = s.lets_confirm_last_name
	u.save()	
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.my_last_name_is_btn.format(u.last_name), callback_data = s.agree)
	keyboard.add(agree_btn)
	bot.send_message(chat_id, s.confirm_last_name.format(u.last_name), reply_markup = keyboard)


def select_sex(chat_id, m = None, c = None):
	if m != None:
		u = User.get(user_id = uid(m))
		u.last_name = m.text
		keyboard = types.InlineKeyboardMarkup()
		bot.edit_message_reply_markup(uid(m), message_id = int(m.message_id) - 1, reply_markup = keyboard)
	else:
		u = User.get(user_id = cid(c))
	u.state = s.sex
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	male_btn = types.InlineKeyboardButton(text = s.male_btn, callback_data = s.male)
	female_btn = types.InlineKeyboardButton(text = s.female_btn, callback_data = s.female)
	keyboard.add(male_btn, female_btn)
	bot.send_message(chat_id, s.male_or_female, reply_markup = keyboard)


def type_age(chat_id, c = None):
	u = User.get(user_id = cid(c))
	u.sex = c.data
	u.state = s.age
	u.save()
	bot.send_message(chat_id, s.type_age)


def incorrect_age(chat_id, m):
	bot.send_message(chat_id, s.incorrect_age)


def type_email(chat_id, m):
	if not check.age(m.text):
		incorrect_age(chat_id, m)
		return False
	u = User.get(user_id = uid(m))
	u.age = check.age(m.text)
	u.state = s.email
	u.save()
	bot.send_message(chat_id, s.type_email)

def incorrect_email(chat_id, m):
	bot.send_message(chat_id, s.incorrect_email)


def video_intro(chat_id, m):
	if not check.email(m.text):
		incorrect_email(chat_id, m)
		return False
	u = User.get(user_id = uid(m))
	u.email = check.email(m.text)
	u.save()
	bot.send_message(chat_id, s.who_we_are.format(s.intro_link)) # отправим видео
																 # и через 5 минут -- продолжаем
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.agree_btn, callback_data = s.agree)			
	keyboard.add(agree_btn)						
	send_message_delay(chat_id, s.are_we_continuing, delay = 5, state = s.video_intro, reply_markup = keyboard)


def present_trainer(chat_id, c):
	u = User.get(user_id = cid(c))
	tes = Trainer.select().order_by(fn.Random()).limit(1)
	for t in tes:
		print(t.first_name)

	u.trainer_id = t.id
	# u.state = s.trainer
	u.save()
	photo = open(t.photo, 'rb')
	bot.send_photo(chat_id, photo, s.your_trainer.format(t.first_name, t.last_name))
	send_message_delay(chat_id, s.what_to_do.format(s.next_3_days), delay = 3, state = s.trainer) # присвоен тренер

	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.agree_btn, callback_data = s.agree)			
	disagree_btn = types.InlineKeyboardButton(text = s.disagree_btn, callback_data = s.disagree)			
	keyboard.add(agree_btn, disagree_btn)	
	send_message_delay(chat_id, s.are_you_ready, delay = 6, state = s.ready, reply_markup = keyboard, disable_notification = True) # "Вы готовы?"


def remind(chat_id, c):
	u = User.get(user_id = cid(c))
	u.state = s.stop
	u.save()
	bot.send_message(chat_id, s.waiting_from_you, parse_mode = 'Markdown')
	send_mail(u.email, s.your_documents, s.your_documents)
	send_message_delay(chat_id, s.fact_finding_remind, delay=3, state = s.stop)

	keyboard = types.InlineKeyboardMarkup()
	continue_btn = types.InlineKeyboardButton(text = s.continue_btn, callback_data = s.agree)
	keyboard.add(continue_btn)
	send_message_delay(chat_id, s.we_sent_mail, delay=5, state = s.remind, reply_markup = keyboard)


def city(chat_id, c):
	u = User.get(user_id = cid(c))
	u.state = s.city
	u.save()
	bot.send_message(chat_id, s.type_city)


def job(chat_id, m):
	u = User.get(user_id = uid(m))
	u.city = m.text
	u.state = s.job
	u.save()
	bot.send_message(chat_id, s.type_job)


def height(chat_id, m):
	u = User.get(user_id = uid(m))
	u.job = m.text
	u.state = s.height
	u.save()
	bot.send_message(chat_id, s.type_height)


def incorrect_height(chat_id):
	bot.send_message(chat_id, s.incorrect_height)


def weight(chat_id, m):
	if not check.height(m.text):
		incorrect_height(chat_id)
		return False
	u = User.get(user_id = uid(m))
	u.height = check.height(m.text)
	u.state = s.weight
	u.save()
	bot.send_message(chat_id, s.type_weight)


def target_weight(chat_id, m):
	u = User.get(user_id = uid(m))
	u.state = s.target_weight
	u.weight = m.text
	u.save()
	bot.send_message(chat_id, s.type_target_weight)


def methodologies(chat_id, m):
	u = User.get(user_id = uid(m))
	# u.state = s.methodologies
	u.target_weight = m.text
	u.save()
	bot.send_message(chat_id, s.thanks_for_answers)
	send_message_delay(chat_id, s.type_methodologies, delay=5, state = s.methodologies)


def most_difficult(chat_id, m):
	u = User.get(user_id = uid(m))
	u.methodologies = m.text
	u.state = s.most_difficult
	u.save()
	bot.send_message(chat_id, s.type_most_difficult)


def was_result(chat_id, m):
	u = User.get(user_id = uid(m))
	u.most_difficult = m.text
	u.state = s.was_result
	u.save()
	bot.send_message(chat_id, s.type_was_result)


def why_fat_again(chat_id, m):
	u = User.get(user_id = uid(m))
	u.was_result = m.text
	u.state = s.why_fat_again
	u.save()
	bot.send_message(chat_id, s.type_why_fat_again)	
	send_message_delay(chat_id, s.waiting_from_you, delay = 10)


















	


# _____________ END ACTIONS



@bot.message_handler(commands = ['init'])
def init(m):
	User.create_table(fail_silently = True)
	# Trainer.create_table(fail_silently = True)
	# Routing.create_table(fail_silently = True)


@bot.message_handler(commands = ['start'])
def start(m):
	# print(m)
	u = User.cog(user_id = uid(m), username = m.from_user.username, first_name = m.from_user.first_name, last_name = m.from_user.last_name)
	# u.state = s.default
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.agree_btn, callback_data = s.agree)
	disagree_btn = types.InlineKeyboardButton(text = s.disagree_btn, callback_data = s.disagree)
	more_btn = types.InlineKeyboardButton(text = s.more_btn, url = "http://1fitchat.ru")
	keyboard.add(agree_btn)
	keyboard.add(disagree_btn)
	keyboard.add(more_btn)
	bot.send_message(uid(m), s.greeting, reply_markup = keyboard, parse_mode = "Markdown")


@bot.callback_query_handler(func=lambda call: True)
def clbck(c):
	chat_id = cid(c)
	u = User.get(user_id = cid(c))
	try:
		r = Routing.get(state = u.state, decision = c.data)
		keyboard = types.InlineKeyboardMarkup()
		bot.edit_message_reply_markup(chat_id = cid(c), message_id = c.message.message_id, reply_markup = keyboard)
		bot.answer_callback_query(callback_query_id = c.id, show_alert = True)

		try: # на случай если action не определён в таблице роутинга
			if u.state != s.stop:
				eval(r.action)(chat_id, c = c)
		except Exception as e:
			print(e)
			print(s.action_not_defined)
	except Exception as e:
		print(e)
	



@bot.message_handler(content_types = ['text'])
def action(m):
	print(m.from_user.username, m.text)
	chat_id = sid(m)
	u = User.cog(user_id = uid(m))
	if u.state == s.canceled:
		return False
	try:
		r = Routing.get(state = u.state, decision = 'text')

		try: # на случай если action не определён в таблице роутинга
			if u.state != s.stop:
				eval(r.action)(chat_id, m = m)
		except Exception as e:
			print(e)
			print(m)
	except Exception as e:
		print(e)
	







if __name__ == '__main__':
	bot.polling(none_stop=True)