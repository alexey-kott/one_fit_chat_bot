from peewee import *
import strings as s
import datetime

db = SqliteDatabase('../db.sqlite3')

class BaseModel(Model):
	class Meta:
		database = db

class User(BaseModel):
	user_id 	   		= IntegerField(unique = True)
	username	   		= TextField(null = True)
	first_name 	   		= TextField(null = True)
	last_name      		= TextField(null = True)
	sex 		   		= TextField(null = True)
	age			   		= IntegerField(null = True)
	email		   		= TextField(null = True)
	state		   		= TextField(default = s.default)
	last_activity  		= DateTimeField(null = True)
	day 		   		= IntegerField(default = 1) # день, на котором находится поциент (всего 3 дня)
	trainer_id     		= IntegerField(null = True, default = 0)
	city 		   		= TextField(null = True)
	job 		   		= TextField(null = True)
	height 		   		= IntegerField(null = True)
	weight		   		= FloatField(null = True)
	target_weight  		= TextField(null = True)
	methodologies  		= TextField(null = True) # какими методиками пользовались
	most_difficult 		= TextField(null = True) # что было самое сложное?
	was_result	   		= TextField(null = True) # был ли результат?
	why_fat_again  		= TextField(null = True) # почему вес снова возвращался, как вы думаете?
	start_fat	   		= TextField(null = True)
	why_fat_now	   		= TextField(null = True)
	hormonals	   		= TextField(null = True)
	analyzes 	   		= TextField(null = True)
	not_eat		   		= TextField(null = True)
	allergy		   		= TextField(null = True)
	fats_in_family 		= TextField(null = True)
	fat_children   		= TextField(null = True)
	relatives_attitude  = TextField(null = True)
	amount_of_walking   = TextField(null = True)
	any_injuries   		= TextField(null = True)
	motivation	   		= TextField(null = True)


	def cog(user_id, username = '', first_name = '', last_name = ''):
		try:
			with db.atomic():
				return User.create(user_id = user_id, username = username, first_name = first_name, last_name = last_name)
		except Exception as e:
			return User.select().where(User.user_id == user_id).get()
			

	def save(self, force_insert=False, only=None):
		self.last_activity = datetime.datetime.utcnow()
		super().save(force_insert, only)

	def clear(self):
		self.day = 1
		self.sex = None 		   		
		self.age = None			   		
		self.email = None		   		
		self.last_activity = None  		
		self.trainer_id = None     		
		self.city = None 		   		
		self.job = None 		   		
		self.height = None 		   		
		self.weight = None		   		
		self.target_weight = None  		
		self.methodologies = None  		
		self.most_difficult = None 		
		self.was_result = None	   		
		self.why_fat_again = None  		
		self.start_fat = None	   		
		self.why_fat_now = None	   		
		self.hormonals = None	   		
		self.analyzes = None 	   		
		self.not_eat = None		   		
		self.allergy = None		   		
		self.fats_in_family = None 		
		self.fat_children = None   		
		self.relatives_attitude = None  
		self.amount_of_walking = None   
		self.any_injuries = None   		
		self.motivation = None	   		
		super().save()



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
	active		= BooleanField(default = False)


class Error(BaseModel):
	message 	= TextField()
	state		= TextField()
	exception 	= TextField()
	timestamp	= DateTimeField(default = datetime.datetime.utcnow)

class Photo(BaseModel):
	user_id		= IntegerField()
	message_id	= IntegerField()
	note 		= TextField(null = True)

	class Meta:
		primary_key = CompositeKey('user_id', 'message_id')


class Message(BaseModel):
	sender		= IntegerField()
	sender_type = TextField(null = True) # client or trainer
	receiver	= IntegerField()
	text 		= TextField()
	msg_type	= TextField(default = 'text')
	timestamp	= DateTimeField(default = datetime.datetime.utcnow)


class Schedule(BaseModel):
	timestamp   = DateTimeField()
	action 		= TextField()
	arguments	= TextField(null = True)

	class Meta:
		primary_key = CompositeKey("timestamp", "action", "arguments")