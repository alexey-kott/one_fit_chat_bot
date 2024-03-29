from django.db import models
from django.db.utils import DEFAULT_DB_ALIAS
import telebot
from bot.config import *
import datetime

bot = telebot.TeleBot(API_TOKEN)

# Create your models here.
class Admin(models.Model):
	login 	 = models.TextField(unique = True)
	password = models.TextField()
	role = models.TextField()

	class Meta:
		db_table = "admin"

class User(models.Model):
	user_id 	   		= models.IntegerField(unique = True)
	username	   		= models.TextField(null = True)
	first_name 	   		= models.TextField(null = True)
	last_name      		= models.TextField(null = True)
	sex 		   		= models.TextField(null = True)
	age			   		= models.IntegerField(null = True)
	email		   		= models.TextField(null = True)
	state		   		= models.TextField(default = 'default')
	last_activity  		= models.DateTimeField(null = True)
	day 		   		= models.IntegerField(default = 1) # день, на котором находится поциент (всего 3 дня)
	archive				= models.BooleanField(default=False) # по окончанию 3-ёхдневной программы юзер отправляется в архив
	trainer_id     		= models.IntegerField(null = True, default = 0)
	city 		   		= models.TextField(null = True)
	job 		   		= models.TextField(null = True)
	height 		   		= models.IntegerField(null = True)
	weight		   		= models.FloatField(null = True)
	target_weight  		= models.TextField(null = True)
	methodologies  		= models.TextField(null = True) # какими методиками пользовались
	most_difficult 		= models.TextField(null = True) # что было самое сложное?
	was_result	   		= models.TextField(null = True) # был ли результат?
	why_fat_again  		= models.TextField(null = True) # почему вес снова возвращался, как вы думаете?
	start_fat	   		= models.TextField(null = True)
	why_fat_now	   		= models.TextField(null = True)
	hormonals	   		= models.TextField(null = True)
	analyzes 	   		= models.TextField(null = True)
	not_eat		   		= models.TextField(null = True)
	allergy		   		= models.TextField(null = True)
	fats_in_family 		= models.TextField(null = True)
	fat_children   		= models.TextField(null = True)
	relatives_attitude  = models.TextField(null = True)
	amount_of_walking   = models.TextField(null = True)
	any_injuries   		= models.TextField(null = True)
	motivation	   		= models.TextField(null = True)

	class Meta:
		db_table = "user"


class Message(models.Model):
	sender		= models.IntegerField()
	sender_type = models.TextField(null = True) # client or trainer
	receiver	= models.IntegerField()
	text 		= models.TextField()
	msg_type	= models.TextField(default = 'text')
	timestamp	= models.DateTimeField(default = datetime.datetime.utcnow)

	class Meta:
		db_table = "message"

	# def save(self, force_insert=False, force_update=False, using=DEFAULT_DB_ALIAS, update_fields=None):
	# 	self.timestamp = datetime.datetime.utcnow()
	# 	super().save(force_insert, force_update, using, update_fields)

	def send_message(self, sender, receiver, text):
		self.sender = sender
		self.receiver = receiver
		self.text = text
		self.save()
		bot.send_message(receiver, text)

class Trainer(models.Model):
	id 			= models.IntegerField(primary_key=True)
	first_name	= models.TextField()
	last_name 	= models.TextField()
	photo 		= models.TextField()
	active		= models.BooleanField(default = False)

	class Meta:
		db_table = "trainer"

class Photo(models.Model):
	user_id		= models.IntegerField()
	message_id	= models.IntegerField()
	note 		= models.TextField(null = True)

	class Meta:
		db_table = "photo"
		unique_together = (('user_id', 'message_id'), )
