import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(toaddr, theme, text, user_id = 0): #onefit.chat@mail.ru : qazwsx123
	fromaddr = "onefit.chat@mail.ru"
	mypass = "qazwsx123"
	 
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
		server.quit()
		return True
	except:
		print("Mail send error")
		server.quit()
		if user_id != 0:
			return False
	

