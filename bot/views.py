from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext


# Create your views here.
from .models import Admin
from .models import User


def index(request):
	print("INDEX")
	return render(request, "bot/index.html")


def auth(request):
	if request.session.get('login', False):
		print('auth')
		return redirect('/admin/')

	form = request.POST
	if len(form) > 0:
		login = form['login']
		password = form['password']
	else:
		return render(request, 'bot/auth.html')
	try:
		admin = Admin.objects.get(username = login)
		if password == admin.password:
			request.session['login'] = login
			context = {
				'login' 			: login
			}
			return redirect('/admin/')
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
	context = {
		'users' : users
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
	return redirect('/')


