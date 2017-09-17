import re

def age(m):
	is_age = re.findall(r'\d{1,2}\s?(лет|год)?', m)
	if len(is_age) > 0:
		age = re.findall(r'\d{1,2}', m)[0]
		return int(age)
	else:
		return 0

def email(m):
	try:
		return re.findall(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', m)[0]
	except:
		return False
