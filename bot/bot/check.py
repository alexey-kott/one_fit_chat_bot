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

def height(m):
	height = 0
	try:
		height = int(re.findall(r'\d{2,3}', m)[0])
		return height
	except:
		try:
			height = int(re.findall(r'\d\.\d{1,2}', m)[0]) * 100
			return height
		except:
			try:
				comma_float = re.findall(r'\d,\d{1,2}', m)[0]
				return int(comma_float.replace(',', '.')) * 100
			except:
				return False

