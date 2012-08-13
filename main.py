# -*- coding: utf-8 -*-

import re
import json
import random
import datetime
import os,os.path
import GUI
import word
import config

class Dict:
	def __init__(self):
		self.words = {}
		self.lesson_words = []

	def get_word_by_key(self, en):
		w = self.words.get(en)
		if w == None:
			w = word.Word()
			self.words[en] = w
		return w

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

	def loaded_words(self, type_pr):
		return [(it, it.get_stat(type_pr)) for it in self.words.values() if it.is_load()]

	def words_statistic(self):
		stat = []
		for it in self.words.values():
			if it.is_load():
				stat.append(it.word_statictic())
		return stat

	def words_for_lesson(self, cnt_study_words, min_percent, min_success_cnt, type_pr):
		learned_words = []
		studied_words = []
		for wrd, stat in self.loaded_words(type_pr):
			if stat.get_total_answer() > 0:
				if stat.get_success_persent() >= min_percent and stat.get_total_answer() >= min_success_cnt:
					learned_words.append(wrd)
				else:
					studied_words.append(wrd)

		# дополняем изучаемыми/изученными словами из другого направления перевода
		if len(studied_words) < cnt_study_words:
			inv_type_pr = word.ru_to_en_write if type_pr == word.en_to_ru_write else word.en_to_ru_write
			for wrd, stat in self.loaded_words(inv_type_pr):
				if stat.get_total_answer() > 0 and wrd not in (learned_words+studied_words):
					studied_words.append(wrd)
					if len(studied_words) == cnt_study_words:
						break

		# дополняем ни разу не изучаемыми словами
		if len(studied_words) < cnt_study_words:
			for wrd, stat in self.loaded_words(type_pr):
				if stat.get_total_answer() == 0:
					studied_words.append(wrd)
					if len(studied_words) == cnt_study_words:
						break

		studied_words.sort(key = lambda it : it.get_stat(type_pr).get_success_persent())
		studied_words = studied_words[:cnt_study_words]

		return learned_words + studied_words

	def calc_word_scores(self, cnt_study_words, min_percent, min_success_cnt, type_pr):
		self.lesson_words    = self.words_for_lesson(cnt_study_words, min_percent, min_success_cnt, type_pr)
		self.cnt_study_words = cnt_study_words
		self.min_percent     = min_percent
		self.min_success_cnt = min_success_cnt
		
		for it in self.lesson_words:
			rating = it.get_stat(type_pr).calc_rating(min_percent, min_success_cnt)
			it.set_rating(rating)

		#normalize		
		max_rating = max([it.get_rating() for it in self.lesson_words])
		for it in self.lesson_words:
			it.set_rating(it.get_rating()/max_rating)

	def save_stat(self, path_to_stat):
		data = {}
		for it in self.words:
			data[it] = self.words[it].pack()
		stat_json = {"version" : 1, "data" : data}
		json.dump(stat_json, open(path_to_stat, "wb"))

	def get_any_word(self):
		while True:
			wrd = random.choice(self.lesson_words)
			if wrd.get_rating() > random.random():
				return wrd

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
	def __init__(self, cfg):
		random.seed()
		self.type_pr       = random.choice([word.en_to_ru_write, word.ru_to_en_write])
		self.dict          = Dict()
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

class App:
	def __init__(self):
		self.cfg = config.Config("config.json")
		self.win = GUI.MainWindow(self.get_dict, self.get_next_practice, self.end_lesson)
		self.win.init_window()
		self.new_lesson()
		self.win.mainloop()

	def new_lesson(self):		
		cfg_dict        = self.cfg.reload()
		self.retry_time = cfg_dict["retry_time"]
		self.lesson     = Lesson(cfg_dict)
		self.get_next_practice()
		self.win.show()

	def end_lesson(self):
		self.lesson.end_lesson()
		self.win.hide()
		self.win.after(self.retry_time*1000, self.new_lesson)

	def get_dict(self):
		return self.lesson.get_dict()

	def get_next_practice(self):
		if self.lesson.is_end_lesson():
			self.end_lesson()
		else:
			self.win.set_stat(self.lesson.get_lesson_stat())
			self.win.set_word(self.lesson.get_next_practice())

def run():
	import singleton
	me = singleton.SingleInstance()
	os.chdir(os.path.dirname(__file__))
	App()

if __name__=="__main__":
	run()