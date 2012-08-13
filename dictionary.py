# -*- coding: utf-8 -*-

import json
import random
import os.path
import word

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