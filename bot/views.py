from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.http import JsonResponse


# Create your views here.
from .models import Admin
from .models import User
from .models import Trainer

import os
import hashlib
import re
from bot.functions import *

def index(request):
	print("INDEX")
	return render(request, "bot/index.html")


def auth(request):
	request.session.modified = True
	if request.session.get('login', False):
		return redirect('/admin/', request)

	form = request.POST
	if len(form) > 0:
		login = form['login']
		password = form['password']
	else:
		return render(request, 'bot/auth.html')
	try:
		admin = Admin.objects.get(login = login)
		if password == admin.password:
			request.session['login'] = login
			request.session['role'] = admin.role
			context = {
				'login' 			: login,
				'role'		   		: admin.role
			}
			return redirect('/admin/', request, context)
		else:
			context = {
				'incorrect_password' : True,
				'login'				 : login
			}
			return render(request, "bot/auth.html", context)
			
	except:
		context = {
			'user_not_found': True,
			'login'			: login
		}
		return render(request, "bot/auth.html", context)

def admin(request):

	if not request.session.get('login', False):
		return redirect('/')

	users = User.objects.all()
	trainers = Trainer.objects.all()

	context = {
		'users' 	: users,
		'trainers'  : trainers
	}
		# print(request.session.get('login'))
		# return render(request, "bot/admin.html")
	# else:
		# return redirect('/')
	return render(request, "bot/admin.html", context)

def deauth(request):
	request.session.modified = True
	if request.session.get('login', False):
		login = request.session.pop('login', '')
	return redirect('/', request)


def add_trainer_photo(request):
	if request.method == 'POST':
		photo = handle_uploaded_file(request.FILES['photo'])
	return JsonResponse({'name' : photo.name})


def handle_uploaded_file(f):
	with open('bot/images/buffer/{}'.format(f), 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)
	return f


def add_trainer(request):
	form = request.POST
	password = genPassword(form['login'], form['email'])
	admin = Admin(login = form['login'], password = password, role = form['role'])
	admin.save()
	photo_name = password[:7]
	ext = re.findall(r'\.[^\.]+$', form['photo_name'])[0]
	photo_name = "{}{}".format(photo_name, ext)
	text = "Вы зарегистрированы тренером. Логин: {}, пароль: {}".format(form['login'], password)
	send_mail(form['email'], 'Вы зарегистрированы тренером', text)
	if form['role'] == 'trainer':
		trainer = Trainer(id = admin.id, first_name = form['firstname'], last_name = form['lastname'], photo = photo_name)
		trainer.save()
	os.rename("bot/images/buffer/{}".format(form['photo_name']), "bot/images/trainers/{}".format(photo_name))
	return redirect('/admin/', request)


def genPassword(login, email):
	le = "{}{}".format(login, email)
	return hashlib.sha224(le.encode("utf-8")).hexdigest()