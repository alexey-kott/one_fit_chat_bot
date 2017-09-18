import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(address, theme, text): #onefit.chat@mail.ru : qazwsx123
	fromaddr = "onefit.chat@mail.ru"
	mypass = "qazwsx123"
	fromaddr = "test_django_app@mail.ru"
	toaddr = address
	 
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "Регистрация"
	 
	body = text
	msg.attach(MIMEText(body, 'plain'))
	 
	server = smtplib.SMTP('smtp.mail.ru', 587)
	server.starttls()
	server.login(fromaddr, mypass)
	text = msg.as_string()
	try:
		server.sendmail(fromaddr, toaddr, text)
	except:
		print("Mail send error")
	server.quit()
