# -*- coding: utf-8 -*-

import json
import os.path
import word
import global_stat
import unittest


class ErrDict(Exception):
	def __init__(self, value, loc_res_msg):
		self.value = value
		self.loc_res_msg = loc_res_msg

	def __str__(self):
		return repr(self.value)


class Dict:
	def __init__(self):
		self.words = {}

	def get_word_by_key(self, en):
		w = self.words.get(en)
		if not w:
			w = self.words[en] = word.Word()
		return w

	def reload_dict_s(self, text):
		self.words = {}
		for it in json.loads(text):
			en = it[0]
			tr = it[1]
			ru = it[2]
			self.get_word_by_key(en).add_value(en, tr, ru)

	def reload_dict(self, path):
		self.reload_dict_s(open(path).read())

	def reload_stat_s(self, text):
		stat_json = json.loads(text)
		version   = stat_json["version"]
		if version != 1:
			raise ErrDict("Error dictionary version", "err_dict_version")
		data      = stat_json["data"]
		for it in data:
			self.get_word_by_key(it).unpack(data[it])

	def reload_stat(self, path):
		if os.path.exists(path):
			self.reload_stat_s(open(path).read())

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
				if stat.get_total_answer() > 0 and wrd not in (learned_words + studied_words):
					studied_words.append(wrd)
					if len(studied_words) == cnt_study_words:
						break

		# дополняем ни разу не изучаемыми словами
		if len(studied_words) < cnt_study_words:
			for wrd, stat in self.loaded_words(type_pr):
				if stat.get_total_answer() == 0 and wrd not in (learned_words + studied_words):
					wrd.set_first()
					studied_words.append(wrd)
					if len(studied_words) == cnt_study_words:
						break

		studied_words.sort(key=lambda it: it.get_stat(type_pr).get_success_persent())
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
		stat_json = {"version": 1, "data": data}
		json.dump(stat_json, open(path_to_stat, "wb"), indent=2)


class DictTestCase(unittest.TestCase):
	def setUp(self):
		self.dict_obj = Dict()

	def create_word_data(self, num):
		return ["en" + str(num), "tr" + str(num), "ru" + str(num)]

	def create_word_stat(self, num):
		key   = "en" + str(num)
		date  = "2012.01"
		stat1 = [num * 1,  num * 10, date + str(num),     num % 2 == 0]
		stat2 = [num * 20, num * 30, date + str(num + 1), num % 2 == 1]
		return [key, {"0": stat1, "1": stat2}]

	def load_dict(self, interval_from, interval_to):
		json_dict = [self.create_word_data(i) for i in range(interval_from, interval_to)]
		self.dict_obj.reload_dict_s(json.dumps(json_dict))

	def load_stat(self, interval_from, interval_to, version):
		json_data = dict([self.create_word_stat(i) for i in range(interval_from, interval_to)])
		json_stat = {"version": version, "data": json_data}
		self.dict_obj.reload_stat_s(json.dumps(json_stat))

	def assertLoad(self, num):
		dt = self.create_word_data(num)
		wrd_info = self.dict_obj.get_word_by_key("en" + str(num)).get_show_info()
		self.assertEqual((dt[0], "[%s]" % dt[1], dt[2]), wrd_info)

	def assertNotLoad(self, num):
		wrd_info = self.dict_obj.get_word_by_key("en" + str(num)).get_show_info()
		self.assertEqual(("", "", ""), wrd_info)

	def assertLoadStat(self, num):
		wrd1 = word.Word()
		wrd1.unpack(self.create_word_stat(num)[1])
		wrd2 = self.dict_obj.get_word_by_key("en" + str(num))
		self.assertEqual(wrd1.get_stat(0), wrd2.get_stat(0))
		self.assertEqual(wrd1.get_stat(1), wrd2.get_stat(1))

	def test_reload_dict(self):
		interval_from = 0
		interval_to   = 5
		self.load_dict(interval_from, interval_to)

		for i in range(interval_from, interval_to):
			self.assertLoad(i)

	def test_reload_dict_err_key(self):
		interval_from = 0
		interval_to   = 5
		self.load_dict(interval_from, interval_to)

		for i in range(interval_to, interval_to * 2):
			self.assertNotLoad(i)

	def test_reload_dict_double_reload(self):
		interval_from1 = 0
		interval_to1   = 5
		self.load_dict(interval_from1, interval_to1)
		interval_from2 = 3
		interval_to2   = 8
		self.load_dict(interval_from2, interval_to2)

		for i in range(interval_from1, interval_from2):
			self.assertNotLoad(i)

		for i in range(interval_from2, interval_to2):
			self.assertLoad(i)

	def test_reload_stat(self):
		interval_from = 0
		interval_to   = 5
		self.load_dict(interval_from, interval_to)
		self.load_stat(interval_from, interval_to, 1)

		for i in range(interval_from, interval_to):
			self.assertLoad(i)
			self.assertLoadStat(i)

	def test_reload_stat_without_word(self):
		interval_from = 0
		interval_to   = 5
		self.load_stat(interval_from, interval_to, 1)

		for i in range(interval_from, interval_to):
			self.assertLoadStat(i)

	def test_reload_stat_double(self):
		interval_from1 = 0
		interval_to1   = 5
		self.load_stat(interval_from1, interval_to1, 1)
		interval_from2 = 3
		interval_to2   = 8
		self.load_stat(interval_from2, interval_to2, 1)

		for i in range(interval_from1, interval_to2):
			self.assertLoadStat(i)

	def test_loaded_words(self):
		interval_from1 = 0
		interval_to1   = 5
		self.load_dict(interval_from1, interval_to1)
		interval_from2 = 3
		interval_to2   = 9
		self.load_stat(interval_from2, interval_to2, 1)

		loaded_words = self.dict_obj.loaded_words(0)
		self.assertEqual(len(loaded_words), len(range(interval_from1, interval_to1)))

		for i, it in enumerate(loaded_words):
			self.assertEqual(it[0].get_show_info()[0], "en" + str(i))

	def test_load_error_dict_ver(self):
		try:
			self.load_stat(0, 1, 2)
			self.fail("except not found")
		except ErrDict:
			pass

if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(DictTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)
