

INSERT INTO routing VALUES 
	('default','agree','confirm_name'),
	('default','disagree','cancel'),
	('lets_confirm_name','agree','confirm_last_name'),
	('lets_confirm_name','text','confirm_last_name'),
	('lets_confirm_last_name','agree','select_sex'),
	('lets_confirm_last_name','text','select_sex'),
	('sex','male','type_age'),
	('sex','female','type_age'),
	('age','text','type_email'),
	('email','text','video_intro'),
	('video_intro','agree', 'present_trainer')
