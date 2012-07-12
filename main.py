# -*- coding: utf-8 -*-

import re
import json
import random
import os,os.path
import GUI

en_to_ru_write = 0
ru_to_en_write = 1

class Word:
	def __init__(self, en_word, transcription, ru_word):
		self.en_word		= en_word
		self.transcription	= "[%s]" % transcription
		self.ru_word		= ru_word
		self.ru_word_list	= map(lambda x : x.strip().lower(), ru_word.split(","))

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

class Practice:
	def __init__(self, lesson, word, type_pr):
		self.lesson  = lesson
		self.word    = word
		self.type_pr = type_pr

	def source_data(self):
		return self.word.source_data(self.type_pr)

	def check(self, answer):
		is_success, right_answer, right_answer_tr = self.word.check(answer, self.type_pr)
		self.lesson.update(is_success)
		return is_success, right_answer, right_answer_tr

class Lesson:
	def __init__(self, type_pr):
		self.type_pr     = type_pr
		self.cnt_success = 0
		self.cnt_error   = 0

	def update(self, is_success):
		if is_success:
			self.cnt_success += 1
		else:
			self.cnt_error += 1

class App:
	def __init__(self):		
		self.win = GUI.MainWindow(self.get_next, self.end_lesson)
		self.win.init_window()
		self.new_lesson()
		self.win.mainloop()

	def reload(self):
		os.chdir(os.path.dirname(__file__))
		config_params    = self.load_config("config.json")
		self.max_success = config_params["words_per_lesson"]
		self.retry_time  = config_params["retry_time"]
		self.words       = self.load_dict(config_params["path_to_dict"])

	def load_config(self, path):
		config_txt = open(path).read()
		config_txt = re.compile(r"/\*.*?\*/", re.DOTALL).sub("", config_txt) # remove comments
		return json.loads(config_txt)

	def load_dict(self, path):
		words = []
		raw_dict = json.loads(open(path).read())
		for it in raw_dict:
			words.append(Word(it[0],it[1],it[2]))
		return words

	def new_lesson(self):
		self.reload()
		self.lesson = Lesson(random.choice([en_to_ru_write, ru_to_en_write]))
		self.get_next()
		self.win.show()

	def end_lesson(self):
		self.win.hide()
		self.win.after(self.retry_time*1000, self.new_lesson)

	def get_next(self):
		if self.max_success == self.lesson.cnt_success:
			self.end_lesson()
		else:
			num = random.randint(0, len(self.words)-1)
			practice = Practice(self.lesson, self.words[num], self.lesson.type_pr)
			self.win.set_stat(self.lesson.cnt_success, self.max_success, self.lesson.cnt_error)
			self.win.set_word(practice)

if __name__=="__main__":
	import singleton
	me = singleton.SingleInstance()
	App()