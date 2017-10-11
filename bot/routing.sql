

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
	('video_intro','agree', 'present_trainer'),
	('ready','agree', 'remind_1'),
	('remind_1','agree', 'city'),
	('remind_1','disagree', 'cancel'),
	('city','text', 'job'),
	('job','text', 'height'),
	('height','text', 'weight'),
	('weight','text', 'target_weight'),
	('target_weight','text', 'methodologies'),
	('methodologies','text', 'most_difficult'),
	('most_difficult','text', 'was_result'),
	('was_result','text', 'why_fat_again'),
	('why_fat_again','text', 'waiting_from_you'),
	('waiting_from_you','text', 'cancel'),
	('day_2','text', 'tolerancy'),
	('tolerancy','agree', 'when_start_fat'),
	('tolerancy','text', 'when_start_fat'),
	('start_fat','text', 'why_fat_now'),
	('why_fat','text', 'hormonals'),
	('hormonals','text', 'last_analyzes'),
	('hormonals','disagree', 'last_analyzes'),
	('last_analyzes','text', 'not_eat'),
	('not_eat','text', 'allergy'),
	('allergy','text', 'day_2_end');


INSERT INTO trainer VALUES
	(1, 'Мария', 'Гришина', './images/trainers/trainer1.jpg'),
	(2, 'Владимир', 'Иванов', './images/trainers/trainer2.jpg'),
	(3, 'Макс', 'Григорьев', './images/trainers/trainer3.jpg');
