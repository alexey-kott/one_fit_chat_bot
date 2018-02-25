import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from os.path import basename
import re
from datetime import datetime

import sqlite3


def send_mail(toaddr, theme, text, files = None, user_id = 0): #onefit.chat@mail.ru : qazwsx123
	fromaddr = "onefit.chat@mail.ru"
	mypass = "qazwsx123"
	 
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "1FitChat"
	 
	body = text
	msg.attach(MIMEText(body))

	for f in files or []:
		with open(f, "rb") as fil:
		    part = MIMEApplication(
		        fil.read(),
		        Name=basename(f)
		    )
		# After the file is closed
		part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
		msg.attach(part)
	 
	server = smtplib.SMTP('smtp.mail.ru', 587)
	server.starttls()
	server.login(fromaddr, mypass)
	text = msg.as_string()
	try:
		server.sendmail(fromaddr, toaddr, text)
		server.quit()
		return True
	except:
		print("Mail send error")
		server.quit()
		if user_id != 0:
			return False
	

def init_routing():
	with open("routing.sql", "r") as f:
		route = f.read()
		route = re.sub(r'\n', '', route)
		route = re.sub(r'\s+', ' ', route)
		conn = sqlite3.connect('../db.sqlite3')
		cursor = conn.cursor()
		cursor.execute("DELETE FROM routing;") # сначала очистим таблицу роутинга
		conn.commit() 

		cursor.execute(route)
		conn.commit()
		conn.close()


def log_routing_error(e):
	with open("../log/routing_error.txt", "a") as f:
		f.write("{} {}\n".format(datetime.now().strftime("%Y:%m:%d %H:%M:%S"), str(e)))