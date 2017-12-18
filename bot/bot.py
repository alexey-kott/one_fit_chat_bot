# -*- coding: utf-8 -*-
#_______ системные модули
import sqlite3 as sqlite
import telebot
import threading # для отложенных сообщений
from multiprocessing import Process
from time import sleep
import re
import ssl
from aiohttp import web
from datetime import datetime, date, time, timedelta
import json
from telebot import types
from peewee import *
from playhouse.sqlite_ext import *
from playhouse.shortcuts import model_to_dict, dict_to_model # для сериализации peewee-объектов во время логирования ошибок
# ______ модули приложения
from config import *
import strings as s # все строки хранятся здесь
import check # различные проверки: правильно ли юзер ввёл рост/вес/etc
from functions import send_mail, init_routing

# импорт моделей
from bot_models import User
from bot_models import Routing
from bot_models import Trainer
from bot_models import Error
from bot_models import Photo
from bot_models import Message
from bot_models import Schedule


# README
#
# Shortcuts:
#	sid 	= sender chat id
#	m 		= message
#	cog 	= create_or_get
#	c 		= call

class TeleBot(telebot.TeleBot):
	def send_message(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None, parse_mode=None, disable_notification=None):
		Message.create(sender = bot_id, sender_type = "bot", receiver = chat_id, text = text)
		super().send_message(chat_id, text, disable_web_page_preview, reply_to_message_id, reply_markup, parse_mode, disable_notification)

		# print('RESPONSE:')
		# print(response)

init_routing()
bot = TeleBot(API_TOKEN)
bot_id = API_TOKEN.split(":")[0]
# db = SqliteDatabase('../db.sqlite3')
# db = SqliteDatabase('bot.db')

sid = lambda m: m.chat.id # лямбды для определения адреса ответа
uid = lambda m: m.from_user.id
cid = lambda c: c.message.chat.id

# _____________ FUNCTIONS



# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


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
def send_message_delay(chat_id, m, state=None, delay = 0, reply_markup=None, disable_notification=None, parse_mode = 'Markdown'):
	u = User.get(user_id = chat_id)
	if state != None:
		u.state = state
	u.save()
	bot.send_message(chat_id, m, reply_markup=reply_markup, parse_mode=parse_mode, disable_notification=disable_notification)


@delay
def send_photo_delay(chat_id, p, state=None, delay = 0, disable_notification=None):
	u = User.get(user_id = chat_id)
	if state != None:
		u.state = state
	u.save()
	bot.send_photo(chat_id, p, disable_notification=disable_notification)

def schedule(dt, action, **kwargs):
	dt = dt.replace(second = 0, microsecond = 0)
	try:
		Schedule.create(timestamp = dt, action = action, arguments = json.dumps(kwargs))
	except Exception as e:
		# print(e)
		pass


# _____________ END FUNCTIONS

# _____________ ACTIONS

def idle(u, m = None, c = None):
	pass


def cancel(u, c = None, m = None):
	u.state = s.canceled
	u.save()
	bot.send_message(u.user_id, s.canceled_course)


def three_days_importance(u, c):
	u.state = s.three_days_importance
	u.save()
	video = open('videos/three_days_importance.mp4', 'rb')
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.looked_btn, callback_data = s.agree)
	keyboard.add(agree_btn)
	bot.send_chat_action(cid(c), 'upload_video')
	bot.send_video(cid(c), video, reply_markup=keyboard)
	# bot.send_message(uid(m), s.who_we_are.format(s.intro_link), reply_markup = keyboard)



def confirm_name(u, c):
	u.state = s.lets_confirm_name
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.my_name_is_btn.format(u.first_name), callback_data = s.agree)
	keyboard.add(agree_btn)
	bot.send_message(cid(c), s.confirm_name.format(u.first_name), reply_markup = keyboard)


def confirm_last_name(u, m = None, c = None): # получает имя (текстом) или подтверждение того, что мы правильно записали его имя
	if m != None:
		chat_id = uid(m)
		u.first_name = m.text
		keyboard = types.InlineKeyboardMarkup()
		bot.edit_message_reply_markup(uid(m), message_id = int(m.message_id) - 1, reply_markup = keyboard)
	else:
		chat_id = cid(c)
	u.state = s.lets_confirm_last_name
	u.save()	
	keyboard = types.InlineKeyboardMarkup()
	if u.last_name != None:
		agree_btn = types.InlineKeyboardButton(text = s.my_last_name_is_btn.format(u.last_name), callback_data = s.agree)
		keyboard.add(agree_btn)
		bot.send_message(chat_id, s.confirm_last_name.format(u.last_name), reply_markup = keyboard)
		return
	bot.send_message(chat_id, s.type_last_name.format(u.last_name), reply_markup = keyboard)


def select_sex(u, m = None, c = None):
	if m != None:
		chat_id = uid(m)
		u.last_name = m.text
		keyboard = types.InlineKeyboardMarkup()
		try:
			bot.edit_message_reply_markup(uid(m), message_id = int(m.message_id) - 1, reply_markup = keyboard)
		except Exception as e:
			# print(e)
			pass
	else:
		chat_id = cid(c)
	u.state = s.sex
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	male_btn = types.InlineKeyboardButton(text = s.male_btn, callback_data = s.male)
	female_btn = types.InlineKeyboardButton(text = s.female_btn, callback_data = s.female)
	keyboard.add(male_btn, female_btn)
	bot.send_message(chat_id, s.male_or_female, reply_markup = keyboard)


def get_acquainted(u, c):
	u.sex = c.data
	u.state = s.acquaintance
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.looked_btn, callback_data = s.agree)
	keyboard.add(agree_btn)
	if u.sex == 'female':
		video = open('videos/acquaintance_women.mp4', 'rb')
	else:
		video = open('videos/acquaintance_men.mp4', 'rb')
	bot.send_chat_action(cid(c), 'upload_video')
	bot.send_video(cid(c), video, reply_markup=keyboard)



def type_age(u, c = None):
	u.sex = c.data
	u.state = s.age
	u.save()
	bot.send_message(cid(c), s.type_age)


def incorrect_age(u, m):
	bot.send_message(uid(m), s.incorrect_age)


def type_email(u, m):
	if not check.age(m.text):
		incorrect_age(u, m)
		return False
	u.age = check.age(m.text)
	u.state = s.email
	u.save()
	bot.send_message(uid(m), s.type_email)


def incorrect_email(m):
	bot.send_message(uid(m), s.incorrect_email)


def video_intro(u, m):
	if not check.email(m.text):
		incorrect_email(m)
		return False
	u.email = check.email(m.text)
	u.state = s.video_intro
	u.save()

	bot.send_message(uid(m), s.what_to_do) 
	video = open('videos/first_three_days.mp4', 'rb')
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.looked_btn, callback_data = s.agree)
	keyboard.add(agree_btn)
	bot.send_chat_action(uid(m), 'upload_video')
	bot.send_video(uid(m), video, reply_markup=keyboard)

	# keyboard = types.InlineKeyboardMarkup()
	# agree_btn = types.InlineKeyboardButton(text = s.looked_btn, callback_data = s.agree)
	# keyboard.add(agree_btn)
	# bot.send_message(uid(m), s.who_we_are.format(s.intro_link), reply_markup = keyboard) # отправим видео
																 # и через 5 минут -- продолжаем

def are_we_continue(u, c):
	u.state = s.after_intro	
	u.save()											 
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.agree_btn, callback_data = s.agree)			
	keyboard.add(agree_btn)						
	bot.send_message(cid(c), s.are_we_continue, reply_markup = keyboard)


def present_trainer(u, c):
	tes = Trainer.select().where(Trainer.active == True).order_by(fn.Random()).limit(1)
	for t in tes:
		pass
		# print(t.first_name)

	u.trainer_id = t.id
	u.state = s.trainer
	u.save()
	photo = open("images/trainers/{}".format(t.photo), 'rb')
	bot.send_photo(cid(c), photo, s.your_trainer.format(t.first_name, t.last_name))

	u.state = s.ready
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.agree_btn, callback_data = s.agree)			
	disagree_btn = types.InlineKeyboardButton(text = s.disagree_btn, callback_data = s.disagree)			
	keyboard.add(agree_btn, disagree_btn)	
	bot.send_message(cid(c), s.are_you_ready, reply_markup = keyboard, disable_notification = True) # "Вы готовы?"


def not_ready(u, c):
	u.state = s.canceled
	u.save()
	bot.send_message(u.user_id, s.canceled_course)


def remind_1(u, c):
	u.state = s.stop
	u.save()
	# img = open("images/system/img4.jpeg", "rb")
	# bot.send_photo(cid(c), img)
	bot.send_message(u.user_id, s.waiting_from_you)

	files = ['files/Анализы.pdf', 'files/Анкета.docx', 'files/Анкета физактивность.docx']
	send_mail(u.email, s.your_documents, s.your_documents, files = files)

	img = open("images/system/img2.jpeg", "rb")
	send_photo_delay(cid(c), img, delay=3, state = s.stop)
	img = open("images/system/img1.jpeg", "rb")
	send_photo_delay(cid(c), img, delay=6, state = s.stop)

	keyboard = types.InlineKeyboardMarkup()
	continue_btn = types.InlineKeyboardButton(text = s.continue_btn, callback_data = s.agree)
	keyboard.add(continue_btn)
	send_message_delay(cid(c), s.we_sent_mail, delay=9, state = s.remind_1, reply_markup = keyboard)


def city(u, c):
	u.state = s.city
	u.save()
	bot.send_message(cid(c), s.type_city)


def job(u, m):
	u.city = m.text
	u.state = s.job
	u.save()
	bot.send_message(uid(m), s.type_job)


def height(u, m):
	u.job = m.text
	u.state = s.height
	u.save()
	bot.send_message(uid(m), s.type_height)


def incorrect_height(chat_id):
	bot.send_message(chat_id, s.incorrect_height)


def weight(u, m):
	if not check.height(m.text):
		incorrect_height(uid(m))
		return False
	u.height = check.height(m.text)
	u.state = s.weight
	u.save()
	bot.send_message(uid(m), s.type_weight)


def incorrect_weight(chat_id):
	bot.send_message(chat_id, s.incorrect_weight)


def target_weight(u, m):
	if not check.weight(m.text):
		incorrect_weight(uid(m))
		return False
	u.state = s.target_weight
	u.weight = m.text
	u.save()
	bot.send_message(uid(m), s.type_target_weight)


def methodologies(u, m):
	# u.state = s.methodologies
	u.target_weight = m.text
	u.save()
	bot.send_message(uid(m), s.thanks_for_answers)
	send_message_delay(uid(m), s.type_methodologies, delay=5, state = s.methodologies)


def most_difficult(u, m):
	u.methodologies = m.text
	u.state = s.most_difficult
	u.save()
	bot.send_message(uid(m), s.type_most_difficult)


def was_result(u, m):
	u.most_difficult = m.text
	u.state = s.was_result
	u.save()
	bot.send_message(uid(m), s.type_was_result)


def why_fat_again(u, m):
	u.was_result = m.text
	u.state = s.why_fat_again
	u.save()
	bot.send_message(uid(m), s.type_why_fat_again)	


def waiting_from_you(u, m):
	u.why_fat_again = m.text
	u.save()
	# u.state = s.waiting_materials
	# u.save()

	# img = open("images/system/img4.jpeg", "rb") # "напоминаем что ждём от вас"
	# bot.send_photo(uid(m), img)
	# поменяли напоминалку на картинке на текстовую
	bot.send_message(u.user_id, s.waiting_from_you)

	# устанавливаем отправку сообщения на 21.00
	dt = datetime.now()
	dt = dt.replace(hour = 21, minute = 0)
	schedule(dt, "thanks_for_efforts", user_id = uid(m))
	dt = dt.replace(minute = 30)
	schedule(dt, "waiting_sticker", user_id = uid(m))
	# send_message_delay(uid(m), s.thanks_for_efforts, delay = 15)

	# keyboard = types.InlineKeyboardMarkup()
	# agree_btn = types.InlineKeyboardButton(text = s.looked_btn, callback_data = s.agree)
	# keyboard.add(agree_btn)
	# send_message_delay(uid(m), s.food_romance, delay = 15, state = s.waiting_materials, reply_markup = keyboard)

# def measurements(u, c):
	# u.state = s.measurements
	keyboard = types.InlineKeyboardMarkup()
	agree_btn = types.InlineKeyboardButton(text = s.looked_btn, callback_data = s.agree)
	keyboard.add(agree_btn)
	send_message_delay(u.user_id, s.measurements_link, delay = 10, state = s.measurements, reply_markup = keyboard)
	send_mail(u.email, "Замеры тела", s.measurements_link)

	dt = datetime.now()
	dt = dt.replace(hour = 10, minute = 0)
	delta = timedelta(days = 1)
	schedule(dt + delta, "day_2", user_id = u.user_id)
	

def thanks_for_efforts(user_id):
	bot.send_message(user_id, s.thanks_for_efforts)

def waiting_sticker(user_id):
	# img = open("images/system/img4.jpeg", "rb") # "напоминаем что ждём от вас"
	# bot.send_photo(user_id, img)
	bot.send_message(user_id, s.waiting_from_you)


# _________ Day 2

def day_2(user_id):
	u = User.get(user_id = user_id)
	u.day = 2
	u.save()
	# bot.send_message(user_id, s.greeting_2)	
	# img = open("images/system/img4.jpeg", "rb") # "напоминаем что ждём от вас"
	# bot.send_photo(user_id, img)
	send_message_delay(user_id, s.day_2_start.format(u.first_name), state = s.day_2, delay = 1)
	# send_message_delay(user_id, s.waiting_from_you, delay = 6)
	send_message_delay(user_id, "Продолжайте присылать фото всего, что Вы едите и пьёте", delay = 6)

def tolerancy(u, m):
	u.state = s.tolerancy
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	looked_btn = types.InlineKeyboardButton(text = s.looked_btn, callback_data = s.agree)
	keyboard.add(looked_btn)
	bot.send_message(uid(m), s.tolerancy_movie, reply_markup = keyboard)

def when_start_fat(u, m = None, c = None):
	if m:
		chat_id = uid(m)
	else:
		chat_id = cid(c)
	u.state = s.start_fat
	u.save()
	bot.send_message(chat_id, s.when_start_fat)

def why_fat_now(u, m):
	u.state = s.why_fat
	u.start_fat = m.text
	u.save()
	bot.send_message(uid(m), s.why_fat_now)

def hormonals(u, m):
	u.state = s.hormonals
	u.why_fat_now = m.text
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	disagree_btn = types.InlineKeyboardButton(text = s.disagree_btn, callback_data = s.disagree)
	keyboard.add(disagree_btn)
	bot.send_message(uid(m), s.hormonal_acception, reply_markup = keyboard)

def last_analyzes(u, m = None, c = None):
	if m != None:
		u.hormonals = m.text
		keyboard = types.InlineKeyboardMarkup()
		try:
			bot.edit_message_reply_markup(uid(m), message_id = int(m.message_id) - 1, reply_markup = keyboard)
		except Exception as e:
			# print(e)
			pass
	u.state = s.last_analyzes
	u.save()
	bot.send_message(u.user_id, s.last_analyzes_and_what)

def not_eat(u, m):
	u.analyzes = m.text
	u.state = s.not_eat
	u.save()
	bot.send_message(uid(m), s.not_eat_products)

def allergy(u, m):
	u.not_eat = m.text
	u.state = s.allergy
	u.save()
	bot.send_message(uid(m), s.any_allergies)


def last_2_day_answer(u, m):
	u.allergy = m.text
	u.state = s.pause 
	u.save()
	bot.send_message(uid(m), s.waiting_photo_1)

	dt = datetime.now()
	dt = dt.replace(hour = 21, minute = 0)
	schedule(dt, "day_2_end", user_id = u.user_id)



def day_2_end(user_id):

	dt = datetime.now()
	dt = dt.replace(hour = 10, minute = 0)
	delta = timedelta(days = 1)
	schedule(dt + delta, "day_3", user_id = user_id)
	# img = open("images/system/img4.jpeg", "rb") # "напоминаем что ждём от вас"
	# send_photo_delay(uid(m), img, state = s.pause, delay = 2)
	bot.send_message(user_id, s.day_2_end)


# _________ Day 3


def day_3(user_id):
	u = User.get(user_id = user_id)
	u.day = 3
	u.save()
	bot.send_message(user_id, s.greeting_3.format(u.first_name))
	# img = open("images/system/img4.jpeg", "rb") # "напоминаем что ждём от вас"
	# send_photo_delay(user_id, img, state = s.day_3, delay = 5)
	send_message_delay(user_id, s.waiting_from_you, state = s.day_3, delay = 5)


def miron_story(u, m): # "КАКОЙ-ТО ФИЛЬМ (история Мирона или ещё что-то)"
	u.state = s.miron_story
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	looked_btn = types.InlineKeyboardButton(text = s.looked_btn, callback_data = s.agree)
	keyboard.add(looked_btn)
	bot.send_message(uid(m), s.look_at_miron_story, reply_markup = keyboard)


def fats_in_family(u, m = None, c = None):
	u.state = s.fats_in_family
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	disagree_btn = types.InlineKeyboardButton(text = s.disagree_btn, callback_data = s.disagree)
	keyboard.add(disagree_btn)
	bot.send_message(u.user_id, s.fats_in_your_family, reply_markup = keyboard)


def fat_children(u, m = None, c = None):
	if m != None:
		u.fats_in_family = m.text
		keyboard = types.InlineKeyboardMarkup()
		try:
			bot.edit_message_reply_markup(uid(m), message_id = int(m.message_id) - 1, reply_markup = keyboard)
		except Exception as e:
			# print(e)
			pass
	u.state = s.fat_children
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	no_children_btn = types.InlineKeyboardButton(text = s.no_children_btn, callback_data = s.disagree)
	keyboard.add(no_children_btn)
	bot.send_message(u.user_id, s.your_fat_children, reply_markup = keyboard)


def relatives_attitude(u, m = None, c = None):
	if m != None:
		u.fat_children = m.text
		keyboard = types.InlineKeyboardMarkup()
		try:
			bot.edit_message_reply_markup(uid(m), message_id = int(m.message_id) - 1, reply_markup = keyboard)
		except Exception as e:
			print(e)
	u.state = s.relatives_attitude
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	support_btn = types.InlineKeyboardButton(text = s.support_btn, callback_data = s.support)
	dissuade_btn = types.InlineKeyboardButton(text = s.dissuade_btn, callback_data = s.dissuade)
	keyboard.add(support_btn)
	keyboard.add(dissuade_btn)
	bot.send_message(u.user_id, s.your_relatives_attitude, reply_markup = keyboard)


def amount_of_walking(u, m = None, c = None):
	if m != None:
		u.relatives_attitude = m.text
		keyboard = types.InlineKeyboardMarkup()
		try:
			bot.edit_message_reply_markup(uid(m), message_id = int(m.message_id) - 1, reply_markup = keyboard)
		except Exception as e:
			print(e)
	else:
		u.relatives_attitude = c.data
	u.state = s.amount_of_walking
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	many_btn = types.InlineKeyboardButton(text = s.many_btn, callback_data = s.many)
	few_btn = types.InlineKeyboardButton(text = s.few_btn, callback_data = s.few)
	middling_btn = types.InlineKeyboardButton(text = s.middling_btn, callback_data = s.middling)
	keyboard.add(many_btn)
	keyboard.add(few_btn)
	keyboard.add(middling_btn)
	bot.send_message(u.user_id, s.your_amount_of_walking, reply_markup = keyboard)


def any_injuries(u, m = None, c = None):
	if m != None:
		u.amount_of_walking = m.text
		keyboard = types.InlineKeyboardMarkup()
		try:
			bot.edit_message_reply_markup(uid(m), message_id = int(m.message_id) - 1, reply_markup = keyboard)
		except Exception as e:
			print(e)
	else:
		u.amount_of_walking = c.data
	u.state = s.any_injuries
	u.save()
	keyboard = types.InlineKeyboardMarkup()
	disagree_btn = types.InlineKeyboardButton(text = s.disagree_btn, callback_data = s.disagree)
	keyboard.add(disagree_btn)
	bot.send_message(u.user_id, s.your_injuries, reply_markup = keyboard)


def motivation(u, m = None, c = None):
	if m != None:
		u.any_injuries = m.text
		keyboard = types.InlineKeyboardMarkup()
		try:
			bot.edit_message_reply_markup(uid(m), message_id = int(m.message_id) - 1, reply_markup = keyboard)
		except Exception as e:
			print(e)
	u.state = s.motivation
	u.save()
	bot.send_message(u.user_id, s.your_motivation)


def final_reminder(u, m):
	u.motivation = m.text
	u.state = s.final
	u.save()
	bot.send_message(uid(m), s.fill_table)
	send_message_delay(uid(m), s.reminder, delay = 5)

	dt = datetime.now()
	dt = dt.replace(hour = 21, minute = 0)
	schedule(dt, "bye_day_3", user_id = u.user_id)


def bye_day_3(user_id):
	u = User(user_id = user_id).get()
	u.day = 0
	u.save()
	bot.send_message(user_id, s.bye_day_3)





	


# _____________ END ACTIONS

@bot.message_handler(commands = ['ping'])
def ping(m):
	bot.send_message(uid(m), "I'm alive")


@bot.message_handler(commands = ['init'])
def init(m):
	User.create_table(fail_silently = True)
	# Trainer.create_table(fail_silently = True)
	# Routing.create_table(fail_silently = True)
	# Error.create_table(fail_silently = True)
	# Photo.create_table(fail_silently = True)
	# Schedule.create_table(fail_silently = True)



@bot.message_handler(commands = ['start'])
def start(m):
	# print(u, m)
	u = User.cog(user_id = uid(m), username = m.from_user.username, first_name = m.from_user.first_name, last_name = m.from_user.last_name)
	u.clear()
	u.state = s.default
	u.save()
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
	u = User.cog(user_id = cid(c))
	Message.create(sender = cid(c), sender_type = "user", receiver = bot_id, text = c.data, msg_type = 'text')
	try:
		r = Routing.get(state = u.state, decision = c.data)
		keyboard = types.InlineKeyboardMarkup()
		bot.edit_message_reply_markup(chat_id = cid(c), message_id = c.message.message_id, reply_markup = keyboard)
		bot.answer_callback_query(callback_query_id = c.id, show_alert = True)

		try: # на случай если action не определён в таблице роутинга
			if u.state != s.stop:
				eval(r.action)(u = u, c = c)
		except Exception as e:
			Error.create(message = c.data, state = u.state, exception = e)
			print(e)
			print(s.action_not_defined)
	except Exception as e:
		Error.create(message = c.data, state = u.state, exception = e)
		print(e)
	



@bot.message_handler(content_types = ['text'])
def action(m):
	chat_id = sid(m)
	u = User.cog(user_id = uid(m))
	Message.create(sender = uid(m), sender_type = "user", receiver = bot_id, text = m.text)
	if u.state == s.canceled:
		return False
	try:
		r = Routing.get(state = u.state, decision = 'text')
		try: # на случай если action не определён в таблице роутинга
			if u.state != s.stop:
				eval(r.action)(u = u, m = m)
		except Exception as e:
			Error.create(message = m.text, state = u.state, exception = e)
			# print(e)
			# print(m)
	except Exception as e:
		Error.create(message = m.text, state = u.state, exception = e)
		print(e)
	

def save_photo(message): # системная функция, не вызывает отправку сообщения в ТГ
	user_id = message.from_user.id
	fileID = message.photo[-1].file_id
	file_info = bot.get_file(fileID)
	downloaded_file = bot.download_file(file_info.file_path)
	photo_name = "{}_{}.jpg".format(user_id, message.message_id)
	with open("./images/photo/{}".format(photo_name), 'wb') as new_file:
		new_file.write(downloaded_file)
		new_file.close()
	return photo_name


@bot.message_handler(content_types = ['photo'])
def photo(m):
	photo_name = save_photo(m)
	Message.create(sender = uid(m), sender_type = "user", receiver = bot_id, text = photo_name, msg_type = 'photo')
	photo = Photo.create(user_id = uid(m), message_id = m.message_id)
	u = User.cog(user_id = uid(m))
	try:
		r = Routing.get(state = u.state, decision = 'photo')
		try: # на случай если action не определён в таблице роутинга
			if u.state != s.stop:
				eval(r.action)(u = u, m = m)
		except Exception as e:
			Error.create(message = m.text, state = u.state, exception = e)
			# print(e)
			# print(m)
	except Exception as e:
		print(e)



class Watcher:
	def __call__(self):
		while True:
			now = datetime.now()
			now = now.replace(microsecond = 0)
			for row in Schedule.select():
				if row.timestamp == now:
					eval(row.action)(**json.loads(row.arguments))
			sleep(1)



if __name__ == '__main__':
	watcher = Watcher()
	w = Process(target = watcher)
	w.start()

	# Remove webhook, it fails sometimes the set if there is a previous webhook
	bot.remove_webhook()


	if LAUNCH_MODE == "DEV":
		bot.polling(none_stop=True)
	elif LAUNCH_MODE == "PROD":
		app = web.Application()
		app.router.add_post('/{token}/', handle)

		
		# Set webhook
		bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
		                certificate=open(WEBHOOK_SSL_CERT, 'r'))

		# Build ssl context
		context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
		context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

		# Start aiohttp server
		web.run_app(
		    app,
		    host=WEBHOOK_LISTEN,
		    port=WEBHOOK_PORT,
		    ssl_context=context,
		)
