# -*- coding: utf-8 -*-

import re
import json
import random
import os,os.path
import GUI

en_to_ru_write = 0
ru_to_en_write = 1

class Word:
	def __init__(self):
		self.en_word		= ""
		self.transcription	= ""
		self.ru_word		= ""
		self.ru_word_list	= []

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

	def get_any_word(self):
		return random.choice(self.words.values())

class Practice:
	def __init__(self, lesson, word, type_pr):
		self.lesson  = lesson
		self.word    = word
		self.type_pr = type_pr

	def source_data(self):
		return self.word.source_data(self.type_pr)

	def check(self, answer):
		is_success, right_answer, right_answer_tr = self.word.check(answer, self.type_pr)
		self.lesson.update_stat(is_success)
		return is_success, right_answer, right_answer_tr

class Lesson:
	def __init__(self, path_to_dict, max_success):
		self.type_pr     = random.choice([en_to_ru_write, ru_to_en_write])
		self.dict        = Dict()
		self.max_success = max_success
		self.cnt_success = 0
		self.cnt_error   = 0
		self.dict.reload_dict(path_to_dict)

	def update_stat(self, is_success):
		if is_success:
			self.cnt_success += 1
		else:
			self.cnt_error += 1

	def get_next_practice(self):
		return Practice(self, self.dict.get_any_word(), self.type_pr)

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
		config_params   = self.load_config("config.json")
		self.retry_time = config_params["retry_time"]
		self.lesson     = Lesson(config_params["path_to_dict"], config_params["words_per_lesson"])
		self.get_next_practice()
		self.win.show()

	def end_lesson(self):
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