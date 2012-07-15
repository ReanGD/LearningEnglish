# -*- coding: utf-8 -*-

import re
import math
import json
import random
import datetime
import os,os.path
import GUI

en_to_ru_write = 0
ru_to_en_write = 1

class Statistic:
	def __init__(self):
		self.success_answer     = 0.0
		self.error_answer       = 0.0
		self.last_lesson_date   = None
		self.last_lesson_result = None

	def get_total_answer(self):
		return self.success_answer+self.error_answer

	def get_success_persent(self):
		total = self.get_total_answer()
		if total > 0:
			return float(self.success_answer)/total*100.0
		else:
			return 0.0

	def calc_rating(self, min_percent, min_success_cnt):
		pers  = self.get_success_persent()
		total = self.get_total_answer()
		
		rating = 100.0 - pers
		# для изученных слов уменьшаем рейтинг
		if pers >= min_percent and total >= min_success_cnt:
			rating /= 3.0
		# чем чаще слово повторяли, тем меньше рейтинг
		rating *= math.exp(-total*0.07)
		# если последний ответ был неправильным увеличиваем рейтинг
		if self.last_lesson_result == False:
			rating *= 1.5
		# чем дольше слово не повторяли, тем выше рейтинг
		days = 0
		if self.last_lesson_date != None:
			days = (datetime.date.today() - datetime.datetime.strptime(self.last_lesson_date, "%Y.%m.%d").date()).days
		rating *= math.log10(days+1.0)+1.0

		return rating

	def update(self, is_success, dt):
		self.last_lesson_date   = dt
		self.last_lesson_result = is_success
		if is_success:
			self.success_answer += 1
		else:
			self.error_answer += 1

	def unpack(self, statistic):
		self.success_answer, self.error_answer, self.last_lesson_date, self.last_lesson_result = statistic

	def pack(self):
		return [self.success_answer, self.error_answer, self.last_lesson_date, self.last_lesson_result]

class Word:
	def __init__(self):
		self.en_word		= ""
		self.transcription	= ""
		self.ru_word		= ""
		self.ru_word_list	= []
		self.rating			= 0
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

	def set_rating(self, value):
		self.rating = value

	def get_rating(self):
		return self.rating

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

	def is_load(self):
		return self.transcription != ""

	def get_stat(self, type_pr):
		return self.stat[type_pr]

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
		self.lesson_words = []

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

	def loaded_words(self, type_pr):
		return [(it, it.get_stat(type_pr)) for it in self.words.values() if it.is_load()]

	def words_for_lesson(self, cnt_study_words, min_percent, min_success_cnt, type_pr):
		learned_words = []
		studied_words = []
		for word, stat in self.loaded_words(type_pr):
			if stat.get_total_answer() > 0:
				if stat.get_success_persent() >= min_percent and stat.get_total_answer() >= min_success_cnt:
					learned_words.append(word)
				else:
					studied_words.append(word)

		# дополняем изучаемыми/изученными словами из другого направления перевода
		if len(studied_words) < cnt_study_words:
			inv_type_pr = ru_to_en_write if type_pr == en_to_ru_write else en_to_ru_write
			for word, stat in self.loaded_words(inv_type_pr):
				if stat.get_total_answer() > 0 and word not in (learned_words+studied_words):
					studied_words.append(word)
					if len(studied_words) == cnt_study_words:
						break

		# дополняем ни разу не изучаемыми словами
		if len(studied_words) < cnt_study_words:
			for word, stat in self.loaded_words(type_pr):
				if stat.get_total_answer() == 0:
					studied_words.append(word)
					if len(studied_words) == cnt_study_words:
						break

		studied_words.sort(key = lambda it : it.get_stat(type_pr).get_success_persent())
		studied_words = studied_words[:cnt_study_words]

		return learned_words + studied_words

	def calc_word_scores(self, cnt_study_words, min_percent, min_success_cnt, type_pr):
		self.lesson_words = self.words_for_lesson(cnt_study_words, min_percent, min_success_cnt, type_pr)
		
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
			word = random.choice(self.lesson_words)
			if word.get_rating() > random.random():
				return word

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
		self.type_pr       = random.choice([en_to_ru_write, ru_to_en_write])
		self.dict          = Dict()
		self.max_success   = cfg["words_per_lesson"]
		self.cnt_success   = 0
		self.cnt_error     = 0
		self.path_to_stat  = cfg["path_to_stat"]
		self.practice_list = []
		self.dict.reload_dict(cfg["path_to_dict"])
		self.dict.reload_stat(cfg["path_to_stat"])
		self.dict.calc_word_scores(cfg["CntStudyWords"], cfg["MinPercent"], cfg["MinSuccessCnt"], self.type_pr)

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
		self.lesson     = Lesson(cfg)
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