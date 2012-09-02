# -*- coding: utf-8 -*-

import json
import os.path
import word
import global_stat

class Dict:
	def __init__(self):
		self.words = {}

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

	def global_statistic(self, min_percent, min_success_cnt):
		stat = global_stat.GlobalStatistic(min_percent, min_success_cnt)
		for it in self.words.values():
			if it.is_load():
				stat.add_word(it, it.get_stat(word.en_to_ru_write), it.get_stat(word.ru_to_en_write))
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

		lesson_words = learned_words + studied_words
		for it in lesson_words:
			rating = it.get_stat(type_pr).calc_rating(min_percent, min_success_cnt)
			it.set_rating(rating)
		return lesson_words

	def save_stat(self, path_to_stat):
		data = {}
		for it in self.words:
			data[it] = self.words[it].pack()
		stat_json = {"version" : 1, "data" : data}
		json.dump(stat_json, open(path_to_stat, "wb"))