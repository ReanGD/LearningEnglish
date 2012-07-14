# -*- coding: utf-8 -*-

import re
import json
import random
import datetime
import os,os.path
import GUI

en_to_ru_write = 0
ru_to_en_write = 1

class Statistic:
	def __init__(self):
		self.success_answer     = 0
		self.error_answer       = 0
		self.last_lesson_time   = None
		self.last_lesson_result = None

	def update(self, is_success, dt):
		self.last_lesson_time   = dt
		self.last_lesson_result = is_success
		if is_success:
			self.success_answer += 1
		else:
			self.error_answer += 1

	def unpack(self, statistic):
		self.success_answer, self.error_answer, self.last_lesson_time, self.last_lesson_result = statistic

	def pack(self):
		return [self.success_answer, self.error_answer, self.last_lesson_time, self.last_lesson_result]

class Word:
	def __init__(self):
		self.en_word		= ""
		self.transcription	= ""
		self.ru_word		= ""
		self.ru_word_list	= []
		self.stat 			= {en_to_ru_write : Statistic(), ru_to_en_write : Statistic()}

	def add_value(self, en_word, transcription, ru_word):
		if self.en_word == "":
			self.en_word		= en_word.strip()
		if self.transcription == "":
			self.transcription	= "[%s]" % transcription.strip()
		if self.ru_word == "":
			self.ru_word		= ru_word.strip()
		else:
			self.ru_word		= "%s, %s" % (self.ru_word, ru_word.strip())
		self.ru_word_list		= map(lambda x : x.strip().lower(), self.ru_word.split(","))

	def source_data(self, type_pr):
		if type_pr == en_to_ru_write:
			return self.en_word, self.transcription
		else:
			return self.ru_word, ""

	def check(self, answer, type_pr):
		answer = answer.strip().lower()
		if type_pr == en_to_ru_write:
			is_success = (answer in self.ru_word_list)
			return is_success, self.ru_word, ""
		else:
			is_success = (answer == self.en_word.strip().lower())
			return is_success, self.en_word, self.transcription

	def update_stat(self, is_success, dt, type_pr):
		self.stat[type_pr].update(is_success, dt)

	def unpack(self, statistic):
		for it in statistic:
			it_int = int(it)
			if it_int not in self.stat.keys():
				self.stat[it_int] = Statistic()
			self.stat[it_int].unpack(statistic[it])

	def pack(self):
		data = {}
		for it in self.stat:
			data[it] = self.stat[it].pack()
		return data

class Dict:
	def __init__(self):
		self.words = {}

	def get_word_by_key(self, en):
		word = self.words.get(en)
		if word == None:
			word = Word()
			self.words[en] = word
		return word

	def reload_dict(self, path_to_dict):
		self.words = {}
		for it in json.load(open(path_to_dict)):
			en = it[0]
			tr = it[1]
			ru = it[2]
			self.get_word_by_key(en).add_value(en, tr, ru)

	def reload_stat(self, path_to_stat):
		if os.path.exists(path_to_stat):
			stat_json = json.load(open(path_to_stat))
			data      = stat_json["data"]
			for it in data:
				self.get_word_by_key(it).unpack(data[it])

	def save_stat(self, path_to_stat):
		data = {}
		for it in self.words:
			data[it] = self.words[it].pack()
		stat_json = {"version" : 1, "data" : data}
		json.dump(stat_json, open(path_to_stat, "wb"))

	def get_any_word(self):
		return random.choice(self.words.values())

class Practice:
	def __init__(self, lesson, word, type_pr):
		self.lesson  = lesson
		self.word    = word
		self.type_pr = type_pr
		self.result  = False

	def source_data(self):
		return self.word.source_data(self.type_pr)

	def update_stat(self, dt):
		self.word.update_stat(self.result, dt, self.type_pr)

	def check(self, answer):
		is_success, right_answer, right_answer_tr = self.word.check(answer, self.type_pr)
		self.result = is_success
		self.lesson.update_stat(is_success)
		return is_success, right_answer, right_answer_tr

class Lesson:
	def __init__(self, path_to_dict, path_to_stat, max_success):
		self.type_pr       = random.choice([en_to_ru_write, ru_to_en_write])
		self.dict          = Dict()
		self.max_success   = max_success
		self.cnt_success   = 0
		self.cnt_error     = 0
		self.path_to_stat  = path_to_stat
		self.practice_list = []
		self.dict.reload_dict(path_to_dict)
		self.dict.reload_stat(path_to_stat)

	def update_stat(self, is_success):
		if is_success:
			self.cnt_success += 1
		else:
			self.cnt_error += 1		

	def end_lesson(self):
		self.dict.reload_stat(self.path_to_stat)

		dt = datetime.datetime.now().strftime("%Y%m%dT%H:%M:%S")
		for it in self.practice_list:
			it.update_stat(dt)

		self.dict.save_stat(self.path_to_stat)

	def get_next_practice(self):
		pr = Practice(self, self.dict.get_any_word(), self.type_pr)
		self.practice_list.append(pr)
		return pr

	def get_lesson_stat(self):
		return (self.cnt_success, self.max_success, self.cnt_error)

	def is_end_lesson(self):
		return self.max_success == self.cnt_success

class App:
	def __init__(self):		
		self.win = GUI.MainWindow(self.get_next_practice, self.end_lesson)
		self.win.init_window()
		self.new_lesson()
		self.win.mainloop()		

	def load_config(self, path):
		config_txt = open(path).read()
		config_txt = re.compile(r"/\*.*?\*/", re.DOTALL).sub("", config_txt) # remove comments
		return json.loads(config_txt)

	def new_lesson(self):		
		cfg             = self.load_config("config.json")
		self.retry_time = cfg["retry_time"]
		self.lesson     = Lesson(cfg["path_to_dict"], cfg["path_to_stat"], cfg["words_per_lesson"])
		self.get_next_practice()
		self.win.show()

	def end_lesson(self):
		self.lesson.end_lesson()
		self.win.hide()
		self.win.after(self.retry_time*1000, self.new_lesson)

	def get_next_practice(self):
		if self.lesson.is_end_lesson():
			self.end_lesson()
		else:
			self.win.set_stat(self.lesson.get_lesson_stat())
			self.win.set_word(self.lesson.get_next_practice())

if __name__=="__main__":
	import singleton
	me = singleton.SingleInstance()
	os.chdir(os.path.dirname(__file__))
	App()