# -*- coding: utf-8 -*-

import random
import datetime
import word
import dictionary

class Practice:
	def __init__(self, lesson, word, type_pr):
		self.lesson    = lesson
		self.word      = word
		self.type_pr   = type_pr
		self.result    = None
		self.is_answer = False

	def source_data(self):
		return self.word.source_data(self.type_pr)

	def update_stat(self, dt):
		if self.result != None:
			self.word.update_stat(self.result, dt, self.type_pr)

	def is_end(self):
		return self.is_answer

	def check(self, user_answer):
		is_success, right_answer = self.word.check(user_answer, self.type_pr)
		self.is_answer = is_success
		if self.result == None:
			self.result = is_success
			self.lesson.update_stat(is_success)
		return is_success, right_answer

class Lesson:
	def __init__(self, cfg):
		random.seed()
		self.type_pr       = random.choice([word.en_to_ru_write, word.ru_to_en_write])
		self.dict          = dictionary.Dict()
		self.max_success   = cfg["words_per_lesson"]
		self.cnt_success   = 0
		self.cnt_error     = 0
		self.path_to_stat  = cfg["path_to_stat"]
		self.practice_list = []
		self.dict.reload_dict(cfg["path_to_dict"])
		self.dict.reload_stat(cfg["path_to_stat"])
		self.dict.calc_word_scores(cfg["CntStudyWords"], cfg["MinPercent"], cfg["MinSuccessCnt"], self.type_pr)

	def get_dict(self):
		return self.dict

	def update_stat(self, is_success):
		if is_success:
			self.cnt_success += 1
		else:
			self.cnt_error += 1		

	def end_lesson(self):
		self.dict.reload_stat(self.path_to_stat)

		dt = datetime.date.today().strftime("%Y.%m.%d")
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