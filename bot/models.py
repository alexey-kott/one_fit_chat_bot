from django.db import models

# Create your models here.
class Admin(models.Model):
	username = models.TextField(unique = True)
	password = models.TextField()
	user_type = models.TextField()

	class Meta:
		db_table = "admin"

class User(models.Model):
	user_id 	   = models.IntegerField(unique = True)
	username	   = models.TextField(null = True)
	first_name 	   = models.TextField(null = True)
	last_name      = models.TextField(default = '')
	sex 		   = models.TextField(null = True)
	age			   = models.IntegerField(null = True)
	email		   = models.TextField(null = True)
	state		   = models.TextField(default = 'default')
	last_activity  = models.DateTimeField(null = True)
	day 		   = models.IntegerField(default = 1) # день, на котором находится поциент (всего 3 дня)
	trainer_id     = models.IntegerField(null = True)
	city 		   = models.TextField(null = True)
	job 		   = models.TextField(null = True)
	height 		   = models.IntegerField(null = True)
	weight		   = models.FloatField(null = True)
	target_weight  = models.TextField(null = True)
	methodologies  = models.TextField(null = True) # какими методиками пользовались
	most_difficult = models.TextField(null = True) # что было самое сложное?
	was_result	   = models.TextField(null = True) # был ли результат?
	why_fat_again  = models.TextField(null = True) # почему вес снова возвращался, как вы думаете?

	class Meta:
		db_table = "user"